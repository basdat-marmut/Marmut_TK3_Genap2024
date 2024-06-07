from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Song, AkunPlaySong, DownloadedSong
from playlist.models import Playlist, UserPlaylist
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from connector.query import query, get_session_info
import logging
from django.db import connection

logger = logging.getLogger(__name__)


def song_list(request):
    songs = query("SELECT * FROM SONG")
    return render(request, 'song/song_list.html', {'songs': songs})

def song_detail(request, song_id):
    song = query(f"SELECT * FROM SONG WHERE id = '{song_id}'")[0]
    is_premium = request.user.is_authenticated and request.user.is_premium
    
    if request.method == 'POST':
        if 'play' in request.POST:
            progress = int(request.POST.get('progress', 0))
            if progress > 70:
                song['total_play'] += 1
                query(f"UPDATE SONG SET total_play = {song['total_play']} WHERE id = '{song_id}'")
                query(f"INSERT INTO AKUN_PLAY_SONG (user_id, song_id, timestamp) VALUES ('{request.user.id}', '{song_id}', '{timezone.now()}')")
        
        elif 'add_to_playlist' in request.POST:
            playlist_id = request.POST.get('playlist')
            playlist = query(f"SELECT * FROM PLAYLIST WHERE id = '{playlist_id}' AND user_id = '{request.user.id}'")
            if playlist:
                if query(f"SELECT * FROM USER_PLAYLIST WHERE playlist_id = '{playlist_id}' AND song_id = '{song_id}'"):
                    message = f"Lagu dengan judul '{song['title']}' sudah ditambahkan di '{playlist['title']}'!"
                else:
                    query(f"INSERT INTO USER_PLAYLIST (playlist_id, song_id) VALUES ('{playlist_id}', '{song_id}')")
                    message = f"Berhasil menambahkan Lagu dengan judul '{song['title']}' ke '{playlist['title']}'!"
                return render(request, 'song/song_detail.html', {'song': song, 'is_premium': is_premium, 'message': message})
        
        elif 'download' in request.POST:
            if is_premium:
                if query(f"SELECT * FROM DOWNLOADED_SONG WHERE user_id = '{request.user.id}' AND song_id = '{song_id}'"):
                    message = f"Lagu dengan judul '{song['title']}' sudah pernah di unduh!"
                else:
                    query(f"INSERT INTO DOWNLOADED_SONG (user_id, song_id, timestamp) VALUES ('{request.user.id}', '{song_id}', '{timezone.now()}')")
                    song['total_download'] += 1
                    query(f"UPDATE SONG SET total_download = {song['total_download']} WHERE id = '{song_id}'")
                    message = f"Berhasil mengunduh Lagu dengan judul '{song['title']}'!"
                return render(request, 'song/song_detail.html', {'song': song, 'is_premium': is_premium, 'message': message})
    
    playlists = query(f"SELECT * FROM PLAYLIST WHERE user_id = '{request.user.id}'")
    return render(request, 'song/song_detail.html', {'song': song, 'is_premium': is_premium, 'playlists': playlists})

@login_required
def play_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    progress = int(request.POST.get('progress', 0))
    if progress > 70:
        song.total_play += 1
        song.save()
        AkunPlaySong.objects.create(user=request.user, song=song)
    return JsonResponse({'status': 'success'})

@login_required
def add_to_playlist(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    if request.method == 'POST':
        playlist_id = request.POST.get('playlist')
        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        UserPlaylist.objects.create(playlist=playlist, song=song)
        return render(request, 'song/message.html', {
            'message': f"Berhasil menambahkan Lagu dengan judul '{song.title}' ke '{playlist.name}'!",
            'playlist_url': reverse('playlist_detail', args=[playlist.id]),
            'song_id': song.id,
        })
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'song/add_to_playlist.html', {'song': song, 'playlists': playlists})

@login_required
def download_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    if request.user.is_premium:
        song.total_download += 1
        song.save()
        DownloadedSong.objects.create(user=request.user, song=song)
        return render(request, 'song/message.html', {
            'message': f"Berhasil mengunduh Lagu dengan judul '{song.title}'!",
            'playlist_url': reverse('downloaded_songs'),
            'song_id': song.id,
        })
    return redirect('song_detail', song_id=song.id)

def downloaded_songs(request):
    ses_info = get_session_info(request)
    if not ses_info:
        return redirect('main:login')

    user_email = ses_info['email']
    downloaded_songs = query(f"""
        SELECT ds.id_song, k.judul AS title, a.nama AS artist, ds.timestamp
        FROM DOWNLOADED_SONG ds
        JOIN SONG s ON ds.id_song = s.id_konten
        JOIN KONTEN k ON s.id_konten = k.id
        JOIN ARTIST ar ON s.id_artist = ar.id
        JOIN AKUN a ON ar.email_akun = a.email
        WHERE ds.email_downloader = '{user_email}'
        ORDER BY ds.timestamp DESC
    """)

    # Logging the query result
    logger.debug(f"Downloaded songs for user {user_email}: {downloaded_songs}")
    print(f"Downloaded songs for user {user_email}: {downloaded_songs}")

    if request.method == 'POST':
        song_id = request.POST.get('song_id')
        song = query(f"SELECT * FROM SONG WHERE id_konten = '{song_id}'")[0]
        query(f"DELETE FROM DOWNLOADED_SONG WHERE email_downloader = '{user_email}' AND id_song = '{song_id}'")
        song['total_download'] -= 1
        query(f"UPDATE SONG SET total_download = {song['total_download']} WHERE id_konten = '{song_id}'")
        return redirect('downloaded_songs')

    return render(request, 'song/downloaded_songs.html', {'downloaded_songs': downloaded_songs})



def search(request):
    query = request.GET.get('query')
    
    results = []
    
    if query:
        songs = Song.objects.filter(title__icontains=query)
        podcasts = podcast.objects.filter(title__icontains=query)
        
        for song in songs:
            results.append({
                'type': 'SONG',
                'title': song.title,
                'by': song.artist,
                'url': reverse('song_detail', args=[song.id])
            })
        for podcast in podcasts:
            results.append({
                'type': 'PODCAST',
                'title': podcast.title,
                'by': podcast.podcaster,
                'url': reverse('podcast_detail', args=[podcast.id])
            })
    
    context = {
        'query': query,
        'results': results
    }
    return render(request, 'main/search_results.html', context)







