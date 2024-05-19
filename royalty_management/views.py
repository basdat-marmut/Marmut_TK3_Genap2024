from django.http import HttpResponse
from connector.query import query, get_session_info
from .models import Album, Song, Label
from .forms import AlbumForm, SongForm
from django.shortcuts import render, redirect, get_object_or_404

# view royalty
def view_royalty(request):
    ses_info = get_session_info(request)
    if not ses_info:
        return render(request, 'view_royalty.html', {'royalty_data': []})
    
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
            ar.email_akun = {email}
            OR EXISTS (
                SELECT 1 
                FROM SONGWRITER_WRITE_SONG sws 
                JOIN SONGWRITER sw ON sws.id_songwriter = sw.id 
                WHERE sw.email_akun = {email} 
                    AND sws.id_song = s.id_konten
            )
            OR a.email_label = {email};
    """)
    return render(request, 'view_royalty.html', {'royalty_data': royalty_data})

# create albums for artist and songwriter
def create_album(request):
    session_info = get_session_info(request)
    #if not session_info or not (session_info['is_artist'] or session_info['is_songwriter']):
        #return HttpResponse("Unauthorized", status=401)
    
    if request.method == 'POST':
        judul_album = request.POST.get('judul_album')
        label = request.POST.get('label')
        judul_lagu = request.POST.get('judul_lagu')
        artist = session_info['email'] if session_info['is_artist'] else request.POST.get('artist')
        songwriters = request.POST.getlist('songwriters')
        genres = request.POST.getlist('genres')
        durasi = request.POST.get('durasi')
        
        # Validasi input
        if not judul_album or not label or not judul_lagu or not artist or not songwriters or not genres or not durasi:
            return HttpResponse("All fields are required.", status=400)
        
        try:
            # Insert album
            query(f"INSERT INTO ALBUM (judul, id_label) VALUES ('{judul_album}', '{label}') RETURNING id")
            album_id = query(f"SELECT id FROM ALBUM WHERE judul='{judul_album}' AND id_label='{label}'")[0]['id']
            
            # Insert song
            song_query = f"INSERT INTO SONG (judul, id_artist, id_album, total_durasi) VALUES ('{judul_lagu}', '{artist}', '{album_id}', {durasi}) RETURNING id_konten"
            song_id = query(song_query)[0]['id_konten']
            
            # Insert songwriters
            for songwriter in songwriters:
                query(f"INSERT INTO SONGWRITER_WRITE_SONG (id_songwriter, id_song) VALUES ('{songwriter}', '{song_id}')")
            
            # Insert genres
            for genre in genres:
                query(f"INSERT INTO GENRE (id_konten, genre) VALUES ('{song_id}', '{genre}')")
            
            return redirect('manage_songs')
        
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)
    
    labels = query("SELECT * FROM LABEL")
    artists = query("SELECT * FROM ARTIST")
    songwriters = query("SELECT * FROM SONGWRITER")
    genres = query("SELECT DISTINCT genre FROM GENRE")
    
    context = {
        'labels': labels,
        'artists': artists,
        'songwriters': songwriters,
        'genres': genres,
    }
    return render(request, 'create_album.html', context)

# view album for artist and songwriter
def view_album(request):
    session_info = get_session_info(request)
    #if not session_info or not (session_info['is_artist'] or session_info['is_songwriter']):
        #return HttpResponse("Unauthorized", status=401)

    user_email = session_info['email']
    albums = query(f"SELECT * FROM ALBUM WHERE id IN (SELECT id_album FROM SONG WHERE id_artist = '{user_email}')")

    context = {
        'albums': albums,
    }
    return render(request, 'view_album.html', context)

def view_album_label(request):
    session_info = get_session_info(request)
    #if not session_info or not (session_info['is_artist'] or session_info['is_songwriter']):
        #return HttpResponse("Unauthorized", status=401)

    user_email = session_info['email']
    albums = query(f"SELECT * FROM ALBUM WHERE id IN (SELECT id_album FROM SONG WHERE id_artist = '{user_email}')")

    context = {
        'albums': albums,
    }
    return render(request, 'view_album_label.html', context)

# delete an album
def delete_album(request, album_id):
    session_info = get_session_info(request)
    #if not session_info or not (session_info['is_artist'] or session_info['is_songwriter']):
        #return HttpResponse("Unauthorized", status=401)
    
    try:
        query(f"DELETE FROM ALBUM WHERE id = '{album_id}'")
        return redirect('view_album')
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)

# view an album detail
def view_album_detail(request, id_album):
    session_info = get_session_info(request)
    #if not session_info or not (session_info['is_artist'] or session_info['is_songwriter']):
        #return HttpResponse("Unauthorized", status=401)

    album = query(f"SELECT * FROM ALBUM WHERE id = '{id_album}'")[0]
    songs = query(f"SELECT * FROM SONG WHERE id_album = '{id_album}'")

    context = {
        'album': album,
        'songs': songs,
    }
    return render(request, 'view_album_detail.html', context)

# create song for artist/songwriter
def create_song(request, album_id):
    session_info = get_session_info(request)
    #if not session_info or not (session_info['is_artist'] or session_info['is_songwriter']):
        #return HttpResponse("Unauthorized", status=401)

    if request.method == 'POST':
        judul_lagu = request.POST.get('judul_lagu')
        artist = session_info['email'] if session_info['is_artist'] else request.POST.get('artist')
        songwriters = request.POST.getlist('songwriters')
        genres = request.POST.getlist('genres')
        durasi = request.POST.get('durasi')

        if not judul_lagu or not artist or not songwriters or not genres or not durasi:
            return HttpResponse("All fields are required.", status=400)

        try:
            # Insert song
            song_query = f"INSERT INTO SONG (judul, id_artist, id_album, durasi) VALUES ('{judul_lagu}', '{artist}', '{album_id}', {durasi}) RETURNING id_konten"
            song_id = query(song_query)[0]['id_konten']

            # Insert songwriters
            for songwriter in songwriters:
                query(f"INSERT INTO SONGWRITER_WRITE_SONG (id_songwriter, id_song) VALUES ('{songwriter}', '{song_id}')")

            # Insert genres
            for genre in genres:
                query(f"INSERT INTO GENRE (id_konten, genre) VALUES ('{song_id}', '{genre}')")

            # Update album song count and total duration
            total_duration_query = f"SELECT SUM(durasi) AS total_durasi FROM SONG WHERE id_album = '{album_id}'"
            total_duration = query(total_duration_query)[0]['total_durasi']
            song_count_query = f"SELECT COUNT(*) AS jumlah_lagu FROM SONG WHERE id_album = '{album_id}'"
            song_count = query(song_count_query)[0]['jumlah_lagu']
            query(f"UPDATE ALBUM SET total_durasi = {total_duration}, jumlah_lagu = {song_count} WHERE id = '{album_id}'")

            return redirect('view_album_detail', album_id=album_id)

        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

    artists = query("""
        SELECT ARTIST.id, AKUN.nama, AKUN.email
        FROM ARTIST
        JOIN AKUN ON ARTIST.email_akun = AKUN.email
    """)

    songwriters = query("""
        SELECT SONGWRITER.id, AKUN.nama, AKUN.email
        FROM SONGWRITER
        JOIN AKUN ON SONGWRITER.email_akun = AKUN.email
    """)

    genres = query("SELECT DISTINCT genre FROM GENRE")
    album = query(f"SELECT judul FROM ALBUM WHERE id = '{album_id}'")[0]

    # Retrieve the name of the logged-in user
    user_name_query = f"SELECT nama FROM AKUN WHERE email = '{session_info['email']}'"
    user_name = query(user_name_query)[0]['nama']

    context = {
        'album_id': album_id,
        'album_title': album['judul'],
        'artists': artists,
        'songwriters': songwriters,
        'genres': genres,
        'is_artist': session_info['is_artist'],
        'is_songwriter': session_info['is_songwriter'],
        'user_name': user_name,
        'user_email': session_info['email']
    }
    return render(request, 'create_song.html', context)


def view_song_detail(request, song_id):
    session_info = get_session_info(request)
    if not session_info:
        return HttpResponse("Unauthorized", status=401)

    song = query(f"SELECT * FROM SONG WHERE id_konten = '{song_id}'")[0]

    context = {
        'song': song,
    }
    return render(request, 'view_song_detail.html', context)


def delete_song(request, song_id):
    session_info = get_session_info(request)
    #if not session_info:
        #return HttpResponse("Unauthorized", status=401)
    
    try:
        song = query(f"SELECT id_album FROM SONG WHERE id_konten = '{song_id}'")[0]
        album_id = song['id_album']
        query(f"DELETE FROM SONG WHERE id_konten = '{song_id}'")
        
        # Update album song count and total duration
        total_duration_query = f"SELECT SUM(durasi) AS total_durasi FROM SONG WHERE id_album = '{album_id}'"
        total_duration = query(total_duration_query)[0]['total_durasi'] or 0
        song_count_query = f"SELECT COUNT(*) AS jumlah_lagu FROM SONG WHERE id_album = '{album_id}'"
        song_count = query(song_count_query)[0]['jumlah_lagu'] or 0
        query(f"UPDATE ALBUM SET total_durasi = {total_duration}, jumlah_lagu = {song_count} WHERE id = '{album_id}'")
        
        return redirect('view_album_detail', album_id=album_id)
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)
