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
from main.views import podetail

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('search/', search, name='search'),
    path('play-song/', play_song, name='play_song'),
    path('play-user-playlist/', play_user_playlist, name='play_user_playlist'),
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
]