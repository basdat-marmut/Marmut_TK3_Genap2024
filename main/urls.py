from django.urls import path
from main.views import show_main
from main.views import show_main,  play_song, play_user_playlist, register_user, register_label, home, login_and_register
from main.views import register , dashboard
from main.views import login_user
from main.views import logout_user
from main.views import search

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('search/', search, name='search'),
    path('play-song/', play_song, name='play_song'),
    path('play-user-playlist/', play_user_playlist, name='play_user_playlist'),
    path('register/user/', register_user, name='register_user'),
    path('register/label/', register_label, name='register_label'),
    path('home/', home, name='home'),
    path('login_and_register/', login_and_register, name='login_and_register'),
    path('dashboard/', dashboard, name='dashboard'),
]