import uuid
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from .models import Paket, Transaction
from connector.query import query, get_session_info

def langganan_paket(request):
    ses_info = get_session_info(request)
    if not ses_info:
        return redirect('main:login')
    
    paket_list = query("SELECT * FROM PAKET")
    context = {'paket_list': paket_list}
    return render(request, 'langganan/langganan_paket.html', context)

def riwayat_transaksi(request):
    ses_info = get_session_info(request)
    if not ses_info:
        return redirect('main:login')
    
    email = ses_info['email']
    transaksi_list = query(f"""
        SELECT t.id, p.jenis, t.timestamp_dimulai, t.timestamp_berakhir, t.metode_bayar, t.nominal
        FROM TRANSACTION t
        JOIN PAKET p ON t.jenis_paket = p.jenis
        WHERE t.email = '{email}'
        ORDER BY t.timestamp_dimulai DESC
    """)
    
    context = {'transaksi_list': transaksi_list}
    return render(request, 'langganan/riwayat_transaksi.html', context)

def pembayaran_paket(request, jenis):
    ses_info = get_session_info(request)
    if not ses_info:
        return redirect('main:login')
    
    email = ses_info['email']
    
    if request.method == 'POST':
        metode_bayar = request.POST.get('metode_bayar')
        paket = query(f"SELECT * FROM PAKET WHERE jenis = '{jenis}'")
        if not paket:
            return redirect('langganan:langganan_paket')
        paket = paket[0]
        
        # Check for existing active subscription
        active_subscription = query(f"SELECT * FROM TRANSACTION WHERE email = '{email}' AND timestamp_berakhir > NOW()")
        if active_subscription:
            return render(request, 'langganan/langganan_paket.html', {'error': 'You already have an active subscription.'})
        
        # Create new transaction
        timestamp_dimulai = timezone.now()
        timestamp_berakhir = timestamp_dimulai + timezone.timedelta(days=int(paket['jenis'].split()[0]) * 30)
        transaction_id = str(uuid.uuid4())  # Generate a unique transaction ID
        
        query(f"""
            INSERT INTO TRANSACTION (id, jenis_paket, email, timestamp_dimulai, timestamp_berakhir, metode_bayar, nominal)
            VALUES ('{transaction_id}', '{jenis}', '{email}', '{timestamp_dimulai}', '{timestamp_berakhir}', '{metode_bayar}', {paket['harga']})
        """)
        
        # Update user to premium
        query(f"DELETE FROM NONPREMIUM WHERE email = '{email}'")
        query(f"INSERT INTO PREMIUM (email) VALUES ('{email}')")
        
        return redirect('langganan:riwayat_transaksi')
    else:
        paket = query(f"SELECT * FROM PAKET WHERE jenis = '{jenis}'")
        if not paket:
            return redirect('langganan:langganan_paket')
        paket = paket[0]
        context = {'paket': paket}
        return render(request, 'langganan/pembayaran_paket.html', context)