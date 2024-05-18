from django.urls import path
from . import views

urlpatterns = [
    path('', views.playlist_list, name='playlist_list'),
    path('create/', views.playlist_create, name='playlist_create'),
    path('<str:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('<str:playlist_id>/update/', views.playlist_update, name='playlist_update'),
    path('<str:playlist_id>/delete/', views.playlist_delete, name='playlist_delete'),
    path('<str:playlist_id>/add-song/', views.add_song_to_playlist, name='add_song_to_playlist'),
    path('<str:playlist_id>/remove-song/<str:song_id>/', views.remove_song_from_playlist, name='remove_song_from_playlist'),
    # path('search/', views.search, name='search'),
]