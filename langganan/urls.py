from django.urls import path
from . import views

urlpatterns = [
    path('langganan_paket/', views.langganan_paket, name='langganan_paket'),
    path('riwayat_transaksi/', views.riwayat_transaksi, name='riwayat_transaksi'),
    path('pembayaran_paket/<str:jenis>/', views.pembayaran_paket, name='pembayaran_paket'),
    path('search/', views.search, name='search'),
]