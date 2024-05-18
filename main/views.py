from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from connector.query import query, get_session_info, get_navbar_info
import uuid
from django.http import HttpResponseRedirect
from django.urls import reverse



def show_main(request):
    return redirect('main:login_and_register')


def register_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        name = request.POST.get('name')
        gender = 1 if request.POST.get('gender') == "male" else 0
        birth_place = request.POST.get('birthplace')
        birth_date = request.POST.get('birthdate')
        city = request.POST.get('city')
        is_artist = 'True' in request.POST.get('is_artist')
        is_songwriter = 'True' in request.POST.get('is_songwriter')
        is_podcaster = 'True' in request.POST.get('is_podcaster')
        
        #CEK APAKAH EMAIL SUDAH TERDAFTAR
        email_exists = query(f"SELECT * FROM AKUN WHERE email = '{email}' UNION SELECT * FROM LABEL WHERE email = '{email}'")
        if len(email_exists)!=0:
            messages.error(request, 'Email already registered!')
            return redirect('main:register_label')
        
        is_verified = is_artist or is_songwriter or is_podcaster 
        pemilik_hak_cipta_id = str(uuid.uuid4())

        query_string = f"""
                INSERT INTO AKUN (email, password, nama, gender, tempat_lahir, tanggal_lahir, is_verified, kota_asal)
                VALUES ('{email}', '{password}', '{name}', {gender}, '{birth_place}', '{birth_date}', {is_verified}, '{city}');
            """

        query_string += f"""
            INSERT INTO NONPREMIUM (email) VALUES ('{email}');
        """
        
        if is_podcaster:
            query_string += f"""
                INSERT INTO PODCASTER (email)
                VALUES ('{email}');
            """
        
        if is_artist or is_songwriter:
            # Insert pemilik hak cipta
            rate_royalti = 0
            query_string += f"""
                INSERT INTO PEMILIK_HAK_CIPTA (id, rate_royalti)
                VALUES ('{pemilik_hak_cipta_id}', {rate_royalti});
            """

        if is_artist:
            artist_uuid = str(uuid.uuid4())
            
            # Insert artist
            query_string += f"""
                INSERT INTO ARTIST (id, email_akun, id_pemilik_hak_cipta)
                VALUES ('{artist_uuid}', '{email}', '{pemilik_hak_cipta_id}');
            """
            
        if is_songwriter:
            songwriter_uuid = str(uuid.uuid4())
            
            
            query_string += f"""
                INSERT INTO SONGWRITER (id, email_akun, id_pemilik_hak_cipta)
                VALUES ('{songwriter_uuid}', '{email}', '{pemilik_hak_cipta_id}');
            """

        res = query(query_string)

        
        if "error" in str(res):
            messages.error(request, 'An error occurred while registering your account. Please try again later.')
            print(res)
        else:
            messages.success(request, 'Registration successful!')
            return redirect('main:login')  
    context = {
        'navbar' : get_navbar_info(request)
    }
    return render(request, 'register_user.html', context)

def register_label(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        contact = request.POST.get('contact')
        name = request.POST.get('name')
        label_uuid = str(uuid.uuid4())
        pemilik_hak_cipta_id = str(uuid.uuid4())
        
        #CEK APAKAH EMAIL SUDAH TERDAFTAR
        email_exists = query(f"SELECT * FROM AKUN WHERE email = '{email}' UNION SELECT * FROM LABEL WHERE email = '{email}'")
        if len(email_exists)!=0:
            messages.error(request, 'Email already registered!')
            return redirect('main:register_label')
        

        # Insert pemilik hak cipta
        rate_royalti = 0
        query_string = f"""
            INSERT INTO PEMILIK_HAK_CIPTA (id, rate_royalti)
            VALUES ('{pemilik_hak_cipta_id}', {rate_royalti});
        """

        # Insert label
        query_string += f"""
                INSERT INTO label (id, nama, email, password, kontak, id_pemilik_hak_cipta) VALUES
                ('{label_uuid}', '{name}', '{email}', '{password}', '{contact}', '{pemilik_hak_cipta_id}');
        """

        res = query(query_string)

        if "error" in str(res):
            messages.error(request, 'An error occurred while registering your account. Please try again later.')
            print(res)
        else:
            messages.success(request, 'Registration successful!')
            return redirect('main:login')  # Redirect to a home or profile page
    context = {
        'navbar' : get_navbar_info(request)
    }
    return render(request, 'register_label.html', context)

def register(request):
    # Simply render the choice page without any logic for POST methods
    context = {
        'navbar' : get_navbar_info(request)
    }
    return render(request, 'register.html', context)

def login_and_register(request):
    context = {
        'navbar' : get_navbar_info(request)
    }
    return render(request, 'login_and_register.html', context)

def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = query(f"SELECT email FROM AKUN WHERE email = '{email}' AND password = '{password}' UNION SELECT email FROM LABEL WHERE email = '{email}' AND password = '{password}'")
        print(user)
        if len(user) == 0:
            messages.error(request, 'Invalid email or password!')
        else:
            #menentukan user type

            is_artist = len(query(f"SELECT * FROM ARTIST WHERE email_akun = '{email}'")) != 0
            is_songwriter = len(query(f"SELECT * FROM SONGWRITER WHERE email_akun = '{email}'")) != 0
            is_podcaster = len(query(f"SELECT * FROM PODCASTER WHERE email = '{email}'")) != 0
            is_premium = len(query(f"SELECT * FROM PREMIUM WHERE email = '{email}'")) != 0
            is_label = len(query(f"SELECT * FROM LABEL WHERE email = '{email}'")) != 0
            

            session_id = str(uuid.uuid4())
            temp = query(f"""INSERT INTO SESSIONS (session_id, email, is_label, is_premium, is_artist, is_songwriter, is_podcaster) 
                  VALUES ('{session_id}', '{email}' , {is_label}, {is_premium}, {is_artist}, {is_songwriter}, {is_podcaster})
                """)
            

            response = redirect('main:dashboard')
            response.set_cookie('session_id', session_id)
            return response
    context = {
        'navbar' : get_navbar_info(request)
    }
    return render(request, 'login.html', context)

def logout_user(request):
    session_id = request.COOKIES.get('session_id')
    if session_id:
        query(f"DELETE FROM SESSIONS WHERE session_id = '{session_id}'")  # Delete session from database


    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('session_id')  # Delete session_id cookie
    return response


def play_song(request, id):
    user = get_session_info(request)
    id_konten = id
    query_string = f"""
    SELECT * FROM 
        (SELECT * FROM SONG WHERE id_konten = '{id_konten}') AS LAGU 
        NATURAL JOIN 
        (SELECT judul AS judul_lagu, tanggal_rilis, tahun, durasi FROM KONTEN WHERE id = '{id_konten}') AS CONTENT
        JOIN
        (SELECT id AS album_id, judul AS judul_album FROM ALBUM) AS ALBUM ON LAGU.id_album = ALBUM.album_id
        JOIN 
        (SELECT id AS artist_id, email_akun FROM ARTIST) AS ARTIST ON LAGU.id_artist = ARTIST.artist_id
        JOIN
        (SELECT email, nama FROM AKUN) AS AKUN ON ARTIST.email_akun = AKUN.email;
    """
    
    genre = query(f"SELECT genre FROM GENRE WHERE id_konten = '{id_konten}'")
    genre = [g['genre'] for g in genre]

    songwriters = query(f"""
        SELECT nama FROM AKUN WHERE email IN 
            (SELECT email_akun FROM SONGWRITER WHERE id IN
                (SELECT id_songwriter FROM SONGWRITER_WRITE_SONG WHERE id_song = '{id_konten}')
            )
    """)

    songwriters = [sw['nama'] for sw in songwriters]

    user_playlist = query(f"SELECT * FROM USER_PLAYLIST WHERE email_pembuat = '{user['email']}'")
    user_playlist = [{'id': p['id_user_playlist'], 'title': p['judul']} for p in user_playlist]

    is_downloaded = query(f"SELECT * FROM DOWNLOADED_SONG WHERE id_song = '{id_konten}' AND email_downloader = '{user['email']}'")
    is_downloaded = len(is_downloaded) > 0

    konten = query(query_string)[0]    

    song_data = {
        'id': konten['id_konten'],
        'title': konten['judul_lagu'],
        'genres': genre,
        'artist': konten['nama'],
        'songwriters': songwriters,
        'duration': konten['durasi'],  
        'release_date': konten['tanggal_rilis'],
        'year': konten['tahun'],
        'album': konten['judul_album'],
        'total_plays': konten['total_play'],  
        'total_downloads': konten['total_download'],  
        'user_playlists': user_playlist,
        'is_downloaded': is_downloaded,
    }
    context = {
        'song': song_data,
        'user': request.user,
        'user_is_premium': user['is_premium'],
        'navbar' : get_navbar_info(request),
    }
    return render(request, 'play_song.html', context)

def download_song(request, id):
    user = get_session_info(request)
    email = user['email']
    id_konten = id
    query_string = f"""
        INSERT INTO DOWNLOADED_SONG (id_song, email_downloader) VALUES ('{id_konten}', '{email}');
    """
    res = query(query_string)
    if "error" in str(res):
        return HttpResponseNotFound("Download Failed")
    else:
        return HttpResponse("Song downloaded successfully!")

def add_song_to_playlist(request):
    id_song = request.POST.get('id_song')
    id_playlist = request.POST.get('id_playlist')

    query_string = f"""
        INSERT INTO PLAYLIST_SONG (id_playlist, id_song) VALUES ((SELECT id_playlist FROM USER_PLAYLIST WHERE id_user_playlist = '{id_playlist}'), '{id_song}');
    """
    res = query(query_string)
    print(res)
    if "error" in str(res):
        return HttpResponseNotFound("Failed to add song to playlist")
    else:
        return redirect('main:play_user_playlist', id=id_playlist)

def user_play_song(request, id):
    user = get_session_info(request)
    id_konten = id
    waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query_string = f"""
        INSERT INTO AKUN_PLAY_SONG (email_pemain, id_song, waktu) VALUES ('{user['email']}', '{id_konten}', '{waktu}');
    """
    res = query(query_string)
    print(res)
    if "error" in str(res):
        return HttpResponseNotFound("Failed to play song")
    else:
        return HttpResponse("Song played successfully!")


def play_user_playlist(request, id):
    id_user_playlist = id
    query_string = f"""
        SELECT *
        FROM USER_PLAYLIST up
        JOIN AKUN a ON up.email_pembuat = a.email
        WHERE up.id_user_playlist = '{id_user_playlist}';        
    """
    playlist = query(query_string)[0]
    query_string = f"""
        SELECT * FROM 
        (SELECT * FROM SONG WHERE id_konten IN 
            (SELECT id_song FROM PLAYLIST_SONG WHERE id_playlist = '{playlist['id_playlist']}')) AS LAGU
        JOIN
        (SELECT id, judul AS judul_lagu, tanggal_rilis, tahun, durasi FROM KONTEN) AS CONTENT
        ON LAGU.id_konten = CONTENT.id
        JOIN
        (SELECT id AS artist_id, email_akun FROM ARTIST) AS ARTIST ON LAGU.id_artist = ARTIST.artist_id
        JOIN
        (SELECT email, nama FROM AKUN) AS AKUN ON ARTIST.email_akun = AKUN.email;
    """
    songs = query(query_string)
    
    songs_data = []
    total_hours = playlist['total_durasi'] // 60
    total_minutes = playlist['total_durasi'] % 60
    for song in songs:
        songs_data.append({
            'title': song['judul_lagu'],
            'artist': song['nama'],
            'duration': song['durasi'],
            'id_song': song['id_konten']
        })
    
    playlist_data = {
        'id': playlist['id_user_playlist'],
        'title': playlist['judul'],
        'creator': playlist['nama'],
        'songs': songs_data,
        'total_duration_hours': total_hours,
        'total_duration_minutes': total_minutes,
        'created_date': playlist['tanggal_dibuat'],
        'description': playlist['deskripsi']
    }
    print(playlist_data)
    context = {
        'playlist': playlist_data,
        'navbar' : get_navbar_info(request),
    }
    
    return render(request, 'play_user_playlist.html', context)

def shuffle_playlist(request, id):
    id_user_playlist = id

    user = get_session_info(request)
    player = user['email']
    query_string = f"""
        
        INSERT INTO AKUN_PLAY_USER_PLAYLIST (email_pemain, id_user_playlist, email_pembuat, waktu)
        SELECT '{player}', id_user_playlist, email_pembuat, current_timestamp
        FROM USER_PLAYLIST
        WHERE id_user_playlist = '{id_user_playlist}';

        
        INSERT INTO AKUN_PLAY_SONG (email_pemain, id_song, waktu)
        SELECT 
            '{player}' AS email_pemain, 
            ps.id_song AS id_song, 
            current_timestamp AS waktu
        FROM 
            PLAYLIST_SONG ps
        JOIN 
            USER_PLAYLIST up ON ps.id_playlist = up.id_playlist
        WHERE 
            up.id_user_playlist = '{id_user_playlist}';
    """
    res = query(query_string)

    if "error" in str(res):
        return HttpResponseNotFound("Failed to shuffle playlist")
    else:
        return HttpResponse("Playlist shuffled successfully!")


def search(request):
    pass
#     query = request.GET.get('query')
    
#     if query:
#         songs = Song.objects.filter(title__icontains=query)
#         podcasts = podcast.objects.filter(title__icontains=query)
#         user_playlists = UserPlaylist.objects.filter(title__icontains=query)
        
#         results = []
#         for song in songs:
#             results.append({
#                 'type': 'SONG',
#                 'title': song.title,
#                 'by': song.artist,
#                 'url': reverse('song_detail', args=[song.id])
#             })
#         for podcast in podcasts:
#             results.append({
#                 'type': 'PODCAST',
#                 'title': podcast.title,
#                 'by': podcast.podcaster,
#                 'url': reverse('podcast_detail', args=[podcast.id])
#             })
#         for playlist in user_playlists:
#             results.append({
#                 'type': 'USER PLAYLIST',
#                 'title': playlist.title,
#                 'by': playlist.user.username,
#                 'url': reverse('playlist_detail', args=[playlist.id])
#             })
#     else:
#         results = []
    
#     context = {
#         'query': query,
#         'results': results
#     }
#     return render(request, 'main/search_results.html', context)



def createpod(request):
    # Logika untuk menampilkan halaman createpod.html
    return render(request, 'createpod.html')


def createpodepisode(request):
    # Logika untuk menampilkan halaman createpod.html
    return render(request, 'createpod_episode.html')



def seechart(request):
    # Logika untuk menampilkan halaman createpod.html
    return render(request, 'seechart.html')

def daily(request):
    return render(request, 'daily.html')

def weekly(request):
    return render(request, 'weekly.html')

def monthly(request):
    return render(request, 'monthly.html')

def yearly(request):
    return render(request, 'yearly.html')


def podetail(request):
    return render(request, "podcastdetail.html")
def home(request):
    #redirect to login and register
    return redirect('main:login_and_register')

def dashboard(request):
    # Get user from session
    ses_info = get_session_info(request)
    email = ses_info['email']
    if not email:
        return redirect('main:login')
    
    user = query(f"SELECT * FROM AKUN WHERE email = '{email}'")[0]
    if ses_info['is_label']:
        user = query(f"SELECT * FROM LABEL WHERE email = '{email}'")[0]
    
    roles = []
    if ses_info['is_label']:
        roles.append("Label")
    if ses_info['is_artist']:
        roles.append("Artist")
    if ses_info['is_songwriter']:
        roles.append("Songwriter")
    if ses_info['is_podcaster']:
        roles.append("Podcaster")
    roles.append("Pengguna")
    role_str = ", ".join(roles)

    if ses_info['is_label']:
        album_list = query(f"SELECT * FROM ALBUM JOIN LABEL ON ALBUM.id_label = LABEL.id WHERE LABEL.email = '{email}'")
        album_list = [{'title': album['judul'], 'release_date': album['tanggal_rilis']} for album in album_list]
    else:
        album_list = []

    if ses_info['is_podcaster']:
        podcasts = query(f"SELECT * FROM PODCAST JOIN KONTEN ON PODCAST.id_konten = KONTEN.id WHERE PODCAST.email_podcaster = '{email}'")
        podcasts = [{'title': podcast['judul'], 'release_date': podcast['tanggal_rilis'], 'durasi': podcast['durasi']} for podcast in podcasts]
    else:
        podcasts = []
    
    if ses_info['is_artist']:
        songs_artist = query(f"SELECT judul, tanggal_rilis, durasi  FROM SONG JOIN KONTEN ON SONG.id_konten = KONTEN.id JOIN ARTIST ON ARTIST.id = SONG.id_artist WHERE ARTIST.email_akun = '{email}'")
        print(songs_artist)
        songs_artist = [{'title': song['judul'], 'release_date': song['tanggal_rilis'], 'durasi': song['durasi']} for song in songs_artist]
    else:
        songs_artist = []
    
    if ses_info['is_songwriter']:
        songs_songwriter = query(f"SELECT * FROM KONTEN WHERE KONTEN.id IN (SELECT id_song FROM SONGWRITER_WRITE_SONG WHERE SONGWRITER_WRITE_SONG.id_songwriter = (SELECT id FROM SONGWRITER WHERE email_akun = '{email}'))")
        songs_songwriter = [{'title': song['judul'], 'release_date': song['tanggal_rilis'], 'durasi': song['durasi']} for song in songs_songwriter]
    else:
        songs_songwriter = []
    
    songs = songs_artist + songs_songwriter

    playlists = query(f"""
        SELECT * FROM USER_PLAYLIST up
        JOIN AKUN a ON up.email_pembuat = a.email
        WHERE up.email_pembuat = '{email}';
    """)
    print(playlists)
    playlists = [{'title': playlist['judul'], 'created_at': playlist['tanggal_dibuat'], 'song_count': playlist['jumlah_lagu'], 'total_duration': playlist['total_durasi']} for playlist in playlists]

    user = {
        'name': user['nama'],
        'email': user['email'],
        'city': user['kota_asal'],
        'gender': user['gender'],
        'birth_place': user['tempat_lahir'],
        'birth_date': user['tanggal_lahir'],
        'role': role_str,
        'playlists': playlists,
        'songs': songs,
        'podcasts': podcasts,
        'albums': album_list,
    }

    context = {
        'user': user,
        'user_type': 'user',
        'navbar' : get_navbar_info(request),
    }
    return render(request, 'dashboard.html', context)
