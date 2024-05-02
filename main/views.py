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
        username = request.POST.get('email')
        password = make_password(request.POST.get('password'))
        user = User.objects.create(username=username, email=username, password=password)
        
        birth_date = request.POST.get('birthdate')
        city = request.POST.get('city')
        is_artist = 'Artist' in request.POST.get('role', [])
        is_songwriter = 'Songwriter' in request.POST.get('role', [])
        is_podcaster = 'Podcaster' in request.POST.get('role', [])
        
        UserProfile.objects.create(
            user=user,
            birth_date=birth_date,
            city=city,
            is_artist=is_artist,
            is_songwriter=is_songwriter,
            is_podcaster=is_podcaster
        )
        
        login(request, user)  # Automatically log in the new user
        return redirect('main:home')  # Redirect to a home or profile page

    return render(request, 'register_user.html')

def register_label(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = make_password(request.POST.get('password'))
        user = User.objects.create(username=username, email=username, password=password)
        
        contact = request.POST.get('contact')
        
        LabelProfile.objects.create(
            user=user,
            contact=contact
        )
        
        login(request, user)  # Automatically log in the new user
        return redirect('main:home')  # Redirect to a home or profile page

    return render(request, 'register_label.html')

def register(request):
    # Simply render the choice page without any logic for POST methods
    return render(request, 'register.html')

def login_and_register(request):
    return render(request, 'login_and_register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            response = redirect('main:show_main')
            response.set_cookie('last_login', str(datetime.datetime.now()))  # Set the time of last login
            return response
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
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

from django.shortcuts import render
from datetime import datetime, timedelta

def dashboard(request):
    # Dummy data untuk pengguna
    user = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'city': 'New York',
        'gender': 'Male',
        'birth_place': 'Los Angeles',
        'birth_date': '1990-05-15',
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
