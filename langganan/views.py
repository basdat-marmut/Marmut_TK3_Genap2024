from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Paket, Transaction
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def langganan_paket(request):
    paket_list = Paket.objects.all()
    context = {'paket_list': paket_list}
    return render(request, 'langganan/langganan_paket.html', context)

@login_required
def riwayat_transaksi(request):
    transaksi_list = Transaction.objects.filter(email=request.user).order_by('-timestamp_dimulai')
    context = {'transaksi_list': transaksi_list}
    return render(request, 'langganan/riwayat_transaksi.html', context)

@login_required
def pembayaran_paket(request, jenis):
    if request.method == 'POST':
        metode_bayar = request.POST.get('metode_bayar')
        paket = Paket.objects.get(jenis=jenis)
        # Proses pembayaran
        transaction = Transaction.objects.create(
            jenis_paket=paket,
            email=request.user,
            timestamp_dimulai=timezone.now(),
            timestamp_berakhir=timezone.now() + timezone.timedelta(days=30),  # Contoh: 30 hari
            metode_bayar=metode_bayar,
            nominal=paket.harga
        )
        return redirect('riwayat_transaksi')
    else:
        paket = Paket.objects.get(jenis=jenis)
        context = {'paket': paket}
        return render(request, 'langganan/pembayaran_paket.html', context)
    
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