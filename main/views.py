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
from playlist.models import Song, UserPlaylist
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import UserProfile, LabelProfile
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from connector.query import query, get_session_info
import uuid
from django.http import HttpResponseRedirect
from django.urls import reverse


def get_user_type(user):
    try:
        user_profile = user.userprofile
        if user_profile.is_artist:
            return 'artist'
        elif user_profile.is_songwriter:
            return 'songwriter'
        elif user_profile.is_podcaster:
            return 'podcaster'
        else:
            return 'user'
    except UserProfile.DoesNotExist:
        try:
            label_profile = user.labelprofile
            return 'label'
        except LabelProfile.DoesNotExist:
            return 'guest'

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

    return render(request, 'register_user.html')

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

    return render(request, 'register_label.html')

def register(request):
    # Simply render the choice page without any logic for POST methods
    return render(request, 'register.html')

def login_and_register(request):
    return render(request, 'login_and_register.html')

def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = query(f"SELECT * FROM AKUN WHERE email = '{email}' AND password = '{password}' UNION SELECT * FROM LABEL WHERE email = '{email}' AND password = '{password}'")
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

    return render(request, 'login.html')

def logout_user(request):
    session_id = request.COOKIES.get('session_id')
    if session_id:
        query(f"DELETE FROM SESSIONS WHERE session_id = '{session_id}'")  # Delete session from database


    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('session_id')  # Delete session_id cookie
    return response


def play_song(request):
    song_data = {
        'title': 'Blinding Lights',
        'genres': ['Pop', 'Synthwave'],
        'artist': 'The Weeknd',
        'songwriters': ['Abel Tesfaye', 'Ahmad Balshe', 'Jason Quenneville', 'Max Martin', 'Oscar Holter'],
        'duration': 3.22,  
        'release_date': '29/11/2019',
        'year': 2019,
        'album': 'After Hours',
        'total_plays': 2_700_000_000,  
        'total_downloads': 1_000_000  
    }

    return render(request, 'play_song.html', {'song': song_data, 'user': request.user, 'user_is_premium': True})


def play_user_playlist(request):
    songs_data = [
        {'id': 1, 'title': 'Shape of You', 'artist': 'Ed Sheeran', 'duration': '3 minutes 53 seconds', 'play_count': 0},
        {'id': 2, 'title': 'Blinding Lights', 'artist': 'The Weeknd', 'duration': '3 minutes 20 seconds', 'play_count': 0},
        {'id': 3, 'title': 'Rolling in the Deep', 'artist': 'Adele', 'duration': '3 minutes 48 seconds', 'play_count': 0},
        {'id': 4, 'title': 'Bad Guy', 'artist': 'Billie Eilish', 'duration': '3 minutes 14 seconds', 'play_count': 0},
        {'id': 5, 'title': 'Thriller', 'artist': 'Michael Jackson', 'duration': '5 minutes 57 seconds', 'play_count': 0}
    ]

    
    total_seconds = sum(int(song['duration'].split()[0]) * 60 + int(song['duration'].split()[2]) for song in songs_data)
    total_hours = total_seconds // 3600
    total_minutes = (total_seconds % 3600) // 60

    playlist_data = {
        'id': 101,
        'title': 'basdut',
        'creator': 'Lisan Al gaib',
        'songs': songs_data,
        'total_duration_hours': total_hours,
        'total_duration_minutes': total_minutes,
        'created_date': '2024-03-18',
        'description': 'A playlist featuring some of the biggest hits from various artists across genres.'
    }


    return render(request, 'play_user_playlist.html', {'playlist': playlist_data})

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
    # print(ses_info)
    # print("user : ", user)
    # Dummy data untuk pengguna
    # TODO: HANDLE 
    user = {
        'name': user['nama'],
        'email': user['email'],
        'city': user['kota_asal'],
        'gender': user['gender'],
        'birth_place': user['tempat_lahir'],
        'birth_date': user['tanggal_lahir'],
        'role': 'Regular User',
        'playlists': [
            {
                'name': 'Favorite Songs',
                'song_count': 10,
                'created_at': '2023-04-01',
                'total_duration': '1:25:30'
            },
            {
                'name': 'Workout Playlist',
                'song_count': 15,
                'created_at': '2022-12-15',
                'total_duration': '2:10:45'
            },
            {
                'name': 'Chill Vibes',
                'song_count': 8,
                'created_at': '2023-03-20',
                'total_duration': '1:18:12'
            },
        ],
    }

    context = {
        'user': user,
        'user_type': 'user',
    }
    return render(request, 'dashboard.html', context)
