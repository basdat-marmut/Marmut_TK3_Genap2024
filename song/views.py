from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Song, AkunPlaySong, DownloadedSong
from playlist.models import Playlist, UserPlaylist
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from connector.query import query, get_session_info


def song_list(request):
    songs = Song.objects.all()
    return render(request, 'song/song_list.html', {'songs': songs})

def song_detail(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    is_premium = request.user.is_authenticated and request.user.is_premium
    
    if request.method == 'POST':
        if 'play' in request.POST:
            progress = int(request.POST.get('progress', 0))
            if progress > 70:
                song.total_play += 1
                song.save()
                AkunPlaySong.objects.create(user=request.user, song=song, timestamp=timezone.now())
        
        elif 'add_to_playlist' in request.POST:
            playlist_id = request.POST.get('playlist')
            playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
            if UserPlaylist.objects.filter(playlist=playlist, song=song).exists():
                message = f"Lagu dengan judul '{song.title}' sudah ditambahkan di '{playlist.title}'!"
            else:
                UserPlaylist.objects.create(playlist=playlist, song=song)
                message = f"Berhasil menambahkan Lagu dengan judul '{song.title}' ke '{playlist.title}'!"
            return render(request, 'song/song_detail.html', {'song': song, 'is_premium': is_premium, 'message': message})
        
        elif 'download' in request.POST:
            if is_premium:
                if DownloadedSong.objects.filter(user=request.user, song=song).exists():
                    message = f"Lagu dengan judul '{song.title}' sudah pernah di unduh!"
                else:
                    DownloadedSong.objects.create(user=request.user, song=song)
                    song.total_download += 1
                    song.save()
                    message = f"Berhasil mengunduh Lagu dengan judul '{song.title}'!"
                return render(request, 'song/song_detail.html', {'song': song, 'is_premium': is_premium, 'message': message})
    
    playlists = Playlist.objects.filter(user=request.user)
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
    downloaded_songs = DownloadedSong.objects.filter(user__email=user_email).order_by('-timestamp')
    
    if request.method == 'POST':
        song_id = request.POST.get('song_id')
        song = get_object_or_404(Song, id=song_id)
        downloaded_song = get_object_or_404(DownloadedSong, user__email=user_email, song_id=song_id)
        downloaded_song.delete()
        song.total_download -= 1
        song.save()
        messages.success(request, f"Berhasil menghapus Lagu dengan judul '{song.title}' dari daftar unduhan!")
        return redirect('downloaded_songs')
    
    return render(request, 'song/downloaded_songs.html', {'downloaded_songs': downloaded_songs})




def search(request):
    query = request.GET.get('query')
    
    if query:
        songs = Song.objects.filter(title__icontains=query)
        podcasts = podcast.objects.filter(title__icontains=query)
        user_playlists = UserPlaylist.objects.filter(title__icontains=query)
        
        results = []
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
        for playlist in user_playlists:
            results.append({
                'type': 'USER PLAYLIST',
                'title': playlist.title,
                'by': playlist.user.username,
                'url': reverse('playlist_detail', args=[playlist.id])
            })
    else:
        results = []
    
    context = {
        'query': query,
        'results': results
    }
    return render(request, 'main/search_results.html', context)