from django.urls import path
from .views import (
    manage_song_label, view_royalty, manage_song, create_album, view_album, add_song_to_album,
    list_albums_label, view_album_label, delete_album_label, delete_song_label
)

urlpatterns = [
    path('view_royalty/', view_royalty, name='view_royalty'),
    path('manage_song/', manage_song, name='manage_song'),
    path('manage_song_label/', manage_song_label, name='manage_song_label'),
    path('create_album/', create_album, name='create_album'),
    path('album/<int:album_id>/details/', view_album, name='view_album'),
    path('album/<int:album_id>/add_song/', add_song_to_album, name='add_song_to_album'),
    path('albums/', list_albums_label, name='list_albums_label'),
    path('albums/<int:album_id>/', view_album_label, name='view_album_label'),
    path('albums/<int:album_id>/delete/', delete_album_label, name='delete_album_label'),
    path('songs/<int:song_id>/delete/', delete_song_label, name='delete_song_label'),
]