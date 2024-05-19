from django.urls import path
from .views import view_royalty, create_album, create_song, view_album, view_album_label, view_album_detail, view_song_detail, delete_album, delete_song

urlpatterns = [
    path('view_royalty/', view_royalty, name='view_royalty'),
    path('create_album/', create_album, name='create_album'),
    path('create_song/<uuid:album_id>/', create_song, name='create_song'),
    path('view_album/', view_album, name='view_album'),
    path('view_album_label/', view_album_label, name='view_album_label'),
    path('view_album_detail/<uuid:album_id>/', view_album_detail, name='view_album_detail'),
    path('view_song_detail/<uuid:song_id>/', view_song_detail, name='view_song_detail'),
    path('delete_album/<uuid:album_id>/', delete_album, name='delete_album'),
    path('delete_song/<uuid:song_id>/', delete_song, name='delete_song'),
]