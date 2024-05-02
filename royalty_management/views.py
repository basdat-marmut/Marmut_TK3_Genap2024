from django.shortcuts import render, redirect, get_object_or_404
from .models import Album, Song, Label
from .forms import AlbumForm, SongForm

def view_royalties(request):
    return render(request, 'view_royalties.html')

def manage_song(request):
    return render(request, 'manage_song.html')

def manage_song_label(request):
    return render(request, 'manage_song_label.html')

def create_album(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_songs')  
    else:
        form = AlbumForm()
    labels = Label.objects.all()
    return render(request, 'royalty_management/manage_song.html', {'form': form, 'labels': labels})

def view_album(request, album_id):
    album = Album.objects.get(id=album_id)
    songs = album.songs.all()
    return render(request, 'royalty_management/album_detail.html', {'album': album, 'songs': songs})

def add_song_to_album(request, album_id):
    album = Album.objects.get(id=album_id)
    if request.method == 'POST':
        form = SongForm(request.POST)
        if form.is_valid():
            song = form.save(commit=False)
            song.album = album
            song.save()
            return redirect('view_album', album_id=album.id)
    else:
        form = SongForm()
    return render(request, 'royalty_management/add_song.html', {'form': form, 'album': album})

def delete_album(request, album_id):
    album = Album.objects.get(id=album_id)
    album.delete()
    return redirect('manage_songs')

def create_song(request):
    if request.method == 'POST':
        form = SongForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_songs')
    else:
        form = SongForm()
    return render(request, 'royalty_management/manage_song.html', {'form': form})

def list_albums_label(request):
    albums = Album.objects.all()
    return render(request, 'royalty_management/manage_album_label.html', {'albums': albums})

def view_album_label(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    return render(request, 'royalty_management/manage_album_label.html', {'current_album': album, 'albums': Album.objects.all()})

def delete_album_label(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    album.delete()
    return redirect('list_albums_label')

def delete_song_label(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    album_id = song.album.id
    song.delete()
    return redirect('view_album_label', album_id=album_id)
