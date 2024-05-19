from django.urls import path
from main.views import show_main
from main.views import show_main,  play_song, play_user_playlist, register_user, register_label, home, login_and_register
from main.views import register , dashboard
from main.views import login_user
from main.views import logout_user
from main.views import search
from main.views import createpod
from .views import createpodepisode
from main.views import seechart
from main.views import daily
from main.views import weekly
from main.views import monthly
from main.views import yearly
from main.views import song_detail
from main.views import podcastdetail
from main.views import addEpisode
from main.views import deletePodcast
from main.views import download_song, add_song_to_playlist, user_play_song, shuffle_playlist

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('search/', search, name='search'),
    path('play-song/<str:id>/', play_song, name='play_song'),
    path('play-user-playlist/<str:id>/', play_user_playlist, name='play_user_playlist'),    
    path('createpod.html/', createpod, name='createpod'),
    path('createpod.html/createpod_episode.html/', createpodepisode, name='createpodepisode'),
    path('podetail.html/', podetail, name='podetail'),
    path('seechart.html/', seechart, name='seechart'),
    path('seechart.html/daily.html', daily, name='daily'),
    path('seechart.html/weekly.html', weekly, name='weekly'),
    path('seechart.html/monthly.html', monthly, name='monthly'),
    path('seechart.html/yearly.html', yearly, name='yearly'),
    path('register/user/', register_user, name='register_user'),
    path('register/label/', register_label, name='register_label'),
    path('home/', home, name='home'),
    path('login_and_register/', login_and_register, name='login_and_register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('download-song/<str:id>/', download_song, name='download_song'),
    path('add-song-to-playlist/', add_song_to_playlist, name='add_song_to_playlist'),
    path('user-play-song/<str:id>/', user_play_song, name='user_play_song'),
    path('shuffle-playlist/<str:id>/', shuffle_playlist, name='shuffle_playlist'),
    path('song/top/<str:song_judul>/', song_detail, name='song_detail'),
    path('song/daily/', daily, name='daily'),
    path('song/weekly/', weekly, name='weekly'),
    path('song/monthly/', monthly, name='monthly'),
    path('song/yearly/', yearly, name='yearly'),
    path('podcastdetail.html/', podcastdetail, name='podcastdetail'),

    path('createpod/', createpod, name='createpod'),
    path('createpodepisode/', createpodepisode, name='createpodepisode'),
    path('home/createpod_episode/', addEpisode, name='addEpisode'),
    path('deletePodcast/', deletePodcast, name='deletePodcast'),
    path('home/CRUD_daftarepisode.html/', createpodepisode, name='createpodepisode'),
]