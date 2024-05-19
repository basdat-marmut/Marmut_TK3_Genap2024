from connector.query import query, get_session_info
from .models import Album, Song, Label
from .forms import AlbumForm, SongForm
from django.shortcuts import render, redirect, get_object_or_404

def view_royalty(request):
    ses_info = get_session_info(request)
    if not ses_info:
        return render(request, 'royalty_management/view_royalty.html', {'royalty_data': []})
    
    email = ses_info['email']
    royalty_data = query(f"""
        SELECT 
            k.judul AS judul_lagu, 
            a.judul AS judul_album, 
            COALESCE(s.total_play, 0) AS total_play, 
            COALESCE(s.total_download, 0) AS total_download,
            (COALESCE(s.total_play, 0) * phc.rate_royalti) AS total_royalty_didapat
        FROM 
            SONG s
            JOIN KONTEN k ON s.id_konten = k.id
            JOIN ALBUM a ON s.id_album = a.id
            JOIN ARTIST ar ON s.id_artist = ar.id
            JOIN PEMILIK_HAK_CIPTA phc ON ar.id_pemilik_hak_cipta = phc.id
        WHERE 
            ar.email_akun = 'email_anda' 
            OR EXISTS (
                SELECT 1 
                FROM SONGWRITER_WRITE_SONG sws 
                JOIN SONGWRITER sw ON sws.id_songwriter = sw.id 
                WHERE sw.email_akun = 'email_anda' 
                    AND sws.id_song = s.id_konten
            )
            OR a.email_label = 'email_anda';
    """)
    return render(request, 'view_royalty.html', {'royalty_data': royalty_data})

def manage_song(request):
    albums = query("SELECT * FROM ALBUM")
    labels = query("SELECT * FROM LABEL")
    return render(request, 'manage_song.html', {'albums': albums, 'labels': labels})

def manage_song_label(request):
    return render(request, 'manage_song_label.html')

def create_album(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            release_date = form.cleaned_data['release_date']
            label_id = form.cleaned_data['label'].id

            query(f"""
                INSERT INTO ALBUM (title, release_date, label_id)
                VALUES ('{title}', '{release_date}', '{label_id}');
            """)
            return redirect('manage_songs')
    else:
        form = AlbumForm()
    labels = Label.objects.all()
    return render(request, 'manage_song.html', {'form': form, 'labels': labels})

def view_album(request, album_id):
    album = query(f"SELECT * FROM ALBUM WHERE id = '{album_id}'")[0]
    songs = query(f"SELECT * FROM SONG WHERE album_id = '{album_id}'")
    return render(request, 'album_detail.html', {'album': album, 'songs': songs})

def add_song_to_album(request, album_id):
    album = query(f"SELECT * FROM ALBUM WHERE id = '{album_id}'")[0]
    if request.method == 'POST':
        form = SongForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            duration = form.cleaned_data['duration']
            query(f"""
                INSERT INTO SONG (title, duration, album_id)
                VALUES ('{title}', '{duration}', '{album_id}');
            """)
            return redirect('view_album', album_id=album_id)
    else:
        form = SongForm()
    return render(request, 'add_song.html', {'form': form, 'album': album})

def delete_album(request, album_id):
    if request.method == 'POST':
        query(f"DELETE FROM ALBUM WHERE id = '{album_id}'")
        return redirect('manage_songs')
    album = query(f"SELECT * FROM ALBUM WHERE id = '{album_id}'")[0]
    return render(request, '#', {'album': album})

def create_song(request):
    if request.method == 'POST':
        form = SongForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_songs')
    else:
        form = SongForm()
    return render(request, 'manage_song.html', {'form': form})

def list_albums_label(request):
    albums = Album.objects.all()
    return render(request, 'manage_album_label.html', {'albums': albums})

def view_album_label(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    return render(request, 'manage_album_label.html', {'current_album': album, 'albums': Album.objects.all()})

def delete_album_label(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    album.delete()
    return redirect('list_albums_label')

def delete_song_label(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    album_id = song.album.id
    song.delete()
    return redirect('view_album_label', album_id=album_id)
