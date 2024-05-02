from django.urls import path
from main.views import show_main
from main.views import show_main, create_product, show_xml, show_json, show_xml_by_id, show_json_by_id, play_song, play_user_playlist
from main.views import register 
from main.views import login_user
from main.views import logout_user
from main.views import edit_product
from main.views import delete_product
from main.views import get_product_json
from main.views import add_product_ajax
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
    path('create-product', create_product, name='create_product'),
    path('xml/', show_xml, name='show_xml'), 
    path('json/', show_json, name='show_json'), 
    path('xml/<int:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<int:id>/', show_json_by_id, name='show_json_by_id'),    
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('edit-product/<int:id>', edit_product, name='edit_product'),
    path('delete/<int:id>', delete_product, name='delete_product'),
    path('get-product/', get_product_json, name='get_product_json'),
    path('create-product-ajax/', add_product_ajax, name='add_product_ajax'),
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
]