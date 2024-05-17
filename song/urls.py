from django.urls import path
from . import views

urlpatterns = [
    path('', views.song_list, name='song_list'),
    path('<str:song_id>/', views.song_detail, name='song_detail'),
    path('<int:song_id>/play/', views.play_song, name='play_song'),
    path('<int:song_id>/add-to-playlist/', views.add_to_playlist, name='add_to_playlist'),
    path('<int:song_id>/download/', views.download_song, name='download_song'),
    path('downloaded/', views.downloaded_songs, name='downloaded_songs'),
    path('search/', views.search, name='search'),
]
