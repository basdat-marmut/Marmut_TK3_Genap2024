from django.shortcuts import render, redirect, get_object_or_404
from .models import Playlist, Song, UserPlaylist
from .forms import PlaylistForm, UserPlaylistForm

def playlist_list(request):
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'playlist/playlist_list.html', {'playlists': playlists})

def playlist_create(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            return redirect('playlist_list')
    else:
        form = PlaylistForm()
    return render(request, 'playlist/playlist_form.html', {'form': form})

def playlist_update(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    if request.method == 'POST':
        form = PlaylistForm(request.POST, instance=playlist)
        if form.is_valid():
            form.save()
            return redirect('playlist_list')
    else:
        form = PlaylistForm(instance=playlist)
    return render(request, 'playlist/playlist_form.html', {'form': form})

def playlist_delete(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    playlist.delete()
    return redirect('playlist_list')

def playlist_detail(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    songs = UserPlaylist.objects.filter(playlist=playlist)
    return render(request, 'playlist/playlist_detail.html', {'playlist': playlist, 'songs': songs})

def add_song_to_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    if request.method == 'POST':
        form = UserPlaylistForm(request.POST)
        if form.is_valid():
            user_playlist = form.save(commit=False)
            user_playlist.playlist = playlist
            user_playlist.save()
            return redirect('playlist_detail', playlist_id=playlist_id)
    else:
        form = UserPlaylistForm()
    return render(request, 'playlist/add_song_to_playlist.html', {'form': form, 'playlist': playlist})

def remove_song_from_playlist(request, playlist_id, song_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    song = get_object_or_404(Song, id=song_id)
    UserPlaylist.objects.filter(playlist=playlist, song=song).delete()
    return redirect('playlist_detail', playlist_id=playlist_id)