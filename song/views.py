from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Song, AkunPlaySong, DownloadedSong
from playlist.models import Playlist, UserPlaylist
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

def song_list(request):
    songs = Song.objects.all()
    return render(request, 'song/song_list.html', {'songs': songs})

def song_detail(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    is_premium = request.user.is_authenticated and request.user.is_premium
    return render(request, 'song/song_detail.html', {'song': song, 'is_premium': is_premium})

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

@login_required
def downloaded_songs(request):
    songs = DownloadedSong.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'song/downloaded_songs.html', {'songs': songs})


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