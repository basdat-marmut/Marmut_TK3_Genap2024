from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import uuid
from datetime import datetime
from connector.query import query, get_session_info
#httpresponse
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from connector.query import get_session_info, query, get_navbar_info  # Assuming these are custom utility functions
#csrf_exempt
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def playlist_list(request):
    user = get_session_info(request)
    email = user['email']
    if not user:
        return redirect('main:login')
    playlists = query(f"""
        SELECT * FROM USER_PLAYLIST up
        JOIN AKUN a ON up.email_pembuat = a.email
        WHERE up.email_pembuat = '{email}';
    """)
    res_playlist = []
    for playlist in playlists:
        res_playlist.append({
            'name'  : playlist['judul'],
            'description' : playlist['deskripsi'],
            'jumlah_lagu' : playlist['jumlah_lagu'],
            'durasi' : playlist['total_durasi'],
            'tanggal_dibuat' : playlist['tanggal_dibuat'],
            'id' : playlist['id_user_playlist'],
        })
    context = {
        'playlists': res_playlist,
        'navbar': get_navbar_info(request)        
    }
    return render(request, 'playlist/playlist_list.html', context)

@csrf_exempt
def playlist_create(request):
    user = get_session_info(request)
    if not user:
        return redirect('main:login')
    if request.method == 'POST':
        user = get_session_info(request)
        email = user['email']
        name = request.POST['judul']
        description = request.POST['deskripsi']
        new_id = str(uuid.uuid4())
        playlist_id = str(uuid.uuid4())
        current_date = datetime.now().strftime('%Y-%m-%d')

        #inser playlist baru
        query_string = f"""
            INSERT INTO PLAYLIST (id)
            VALUES ('{playlist_id}');
        """

        #insert user_playlist baru
        query_string += f"""
            INSERT INTO USER_PLAYLIST (email_pembuat, id_user_playlist, judul, deskripsi, jumlah_lagu, tanggal_dibuat, id_playlist, total_durasi)
            VALUES ('{email}', '{new_id}', '{name}', '{description}', 0, '{current_date}', '{playlist_id}', 0);
            """

        res = query(query_string)
        if res == 1:
            return redirect('playlist_list')
        
        else:
            print(res)
            return HttpResponseNotFound('Failed to create playlist')
    context = {'ubah': False, 'navbar': get_navbar_info(request)}
    return render(request, 'playlist/playlist_form.html', context)

@csrf_exempt
def playlist_detail(request, playlist_id):
    user = get_session_info(request)
    if not user:
        return redirect('main:login')
    id_user_playlist = playlist_id
    query_string = f"""
        SELECT *
        FROM USER_PLAYLIST up
        JOIN AKUN a ON up.email_pembuat = a.email
        WHERE up.id_user_playlist = '{id_user_playlist}';        
    """
    playlist = query(query_string)[0]
    print(playlist)
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
        'description': playlist['deskripsi'],

    }
    context = {
        'playlist': playlist_data,
        'navbar': get_navbar_info(request)
    }
    return render(request, 'playlist/playlist_detail.html', context)

@csrf_exempt
def remove_song_from_playlist(request, playlist_id, song_id):
    user = get_session_info(request)
    if not user:
        return redirect('main:login')
    query_string = f"""
        DELETE FROM PLAYLIST_SONG
        WHERE id_playlist = 
        (SELECT id_playlist FROM USER_PLAYLIST WHERE id_user_playlist = '{playlist_id}')  AND id_song = '{song_id}';
    """
    res = query(query_string)
    print(res)
    print(query_string)
    if res == 1:
        return redirect('playlist_detail', playlist_id=playlist_id)
    else:
        return HttpResponseNotFound('Failed to remove song from playlist')
    

@csrf_exempt
def add_song_to_playlist(request, playlist_id):
    user = get_session_info(request)
    if not user:
        return redirect('main:login')
    if request.method == 'POST':
        user = get_session_info(request)
        email = user['email']
        song_id = request.POST['lagu']  # Changed to match the form field name

        playlist_id_riil = query(f"""
            SELECT id_playlist FROM USER_PLAYLIST WHERE id_user_playlist = '{playlist_id}';
        """)[0]['id_playlist']
        query_string = f"""
            INSERT INTO PLAYLIST_SONG (id_playlist, id_song)
            VALUES ('{playlist_id_riil}', '{song_id}');
        """
        
        res = query(query_string)
        if res == 1:
            return redirect('playlist_detail', playlist_id=playlist_id)
        else:
            print(res)
            return redirect('add_song_to_playlist', playlist_id=playlist_id)

    all_songs = query(f"""
        SELECT judul, nama, id_konten FROM SONG
        JOIN KONTEN ON SONG.id_konten = KONTEN.id
        JOIN ARTIST ON SONG.id_artist = ARTIST.id
        JOIN AKUN ON ARTIST.email_akun = AKUN.email;
    """)

    songs_data = []
    for song in all_songs:
        songs_data.append({
            'judul': song['judul'],
            'artist': song['nama'],
            'id': song['id_konten']
        })

    context = {
        'songs': songs_data,
        'id': playlist_id,  # Ensuring the correct context variable is passed
        'navbar': get_navbar_info(request) # Added navbar info to context
    }
    return render(request, 'playlist/add_song_to_playlist.html', context)

def playlist_update(request, playlist_id):
    user = get_session_info(request)
    if not user:
        return redirect('main:login')
    if request.method == 'POST':
        user = get_session_info(request)
        email = user['email']
        name = request.POST['judul']
        description = request.POST['deskripsi']

        query_string = f"""
            UPDATE USER_PLAYLIST
            SET judul = '{name}', deskripsi = '{description}'
            WHERE id_user_playlist = '{playlist_id}';
        """

        res = query(query_string)
        if res == 1:
            return redirect('playlist_list')
        else:
            return HttpResponseNotFound('Failed to update playlist')
    context = {'ubah': True, 'id' : playlist_id  , 'navbar': get_navbar_info(request)}
    return render(request, 'playlist/playlist_form.html', context)

@csrf_exempt
def playlist_delete(request, playlist_id):
    user = get_session_info(request)
    if not user:
        return redirect('main:login')
    user_playlist_id = playlist_id
    playlist_id = query(f"""
        SELECT id_playlist FROM USER_PLAYLIST WHERE id_user_playlist = '{user_playlist_id}';
    """)

    playlist_id = playlist_id[0]['id_playlist']
    query_string = f"""
        DELETE FROM PLAYLIST_SONG
        WHERE id_playlist = '{playlist_id}';
    """
    query_string += f"""
        DELETE FROM AKUN_PLAY_USER_PLAYLIST
        WHERE id_user_playlist = '{user_playlist_id}';
    """
    query_string += f"""
        DELETE FROM USER_PLAYLIST
        WHERE id_user_playlist = '{user_playlist_id}';
    """
    query_string += f"""
        DELETE FROM PLAYLIST
        WHERE id = '{playlist_id}';
    """


    res = query(query_string)
    if res == 1:
        return redirect('playlist_list')
    else:
        print(res)
        return HttpResponseNotFound('Failed to delete playlist')

# def playlist_update(request, playlist_id):
#     playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
#     if request.method == 'POST':
#         form = PlaylistForm(request.POST, instance=playlist)
#         if form.is_valid():
#             form.save()
#             return redirect('playlist_list')
#     else:
#         form = PlaylistForm(instance=playlist)
#     return render(request, 'playlist/playlist_form.html', {'form': form})

# def playlist_delete(request, playlist_id):
#     playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
#     playlist.delete()
#     return redirect('playlist_list')

# def add_song_to_playlist(request, playlist_id):
#     playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
#     if request.method == 'POST':
#         form = UserPlaylistForm(request.POST)
#         if form.is_valid():
#             user_playlist = form.save(commit=False)
#             user_playlist.playlist = playlist
#             user_playlist.save()
#             return redirect('playlist_detail', playlist_id=playlist_id)
#     else:
#         form = UserPlaylistForm()
#     return render(request, 'playlist/add_song_to_playlist.html', {'form': form, 'playlist': playlist})

# def remove_song_from_playlist(request, playlist_id, song_id):
#     playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
#     song = get_object_or_404(Song, id=song_id)
#     UserPlaylist.objects.filter(playlist=playlist, song=song).delete()
#     return redirect('playlist_detail', playlist_id=playlist_id)

# def search(request):
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