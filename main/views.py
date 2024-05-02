from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseRedirect
from main.forms import ProductForm
from django.urls import reverse
from main.models import Product
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt


def show_json_by_id(request, id):
    data = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_xml_by_id(request, id):
    data = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json(request):
    data = Product.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_xml(request):
    data = Product.objects.all()
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

@login_required(login_url='/login')
def show_main(request):
    products = Product.objects.filter(user=request.user)
    last_login = request.COOKIES.get('last_login', 'Your first login')  # Provides a default if 'last_login' isn't set

    context = {
        'name': request.user.username,
        'class': 'PBP A',
        'products': products,
        'last_login': last_login,  # Use the safe variable here
    }

    return render(request, "main.html", context)

def create_product(request):
    form = ProductForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        product = form.save(commit=False)
        product.user = request.user
        product.save()
        return HttpResponseRedirect(reverse('main:show_main'))

    context = {'form': form}
    return render(request, "create_product.html", context)

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        print("debug3")
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("debug4")
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            response = redirect('main:show_main')
            response.set_cookie('last_login', str(datetime.datetime.now()))  # Set the time of last login
            return response
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

def edit_product(request, id):
    # Get product berdasarkan ID
    product = Product.objects.get(pk = id)

    # Set product sebagai instance dari form
    form = ProductForm(request.POST or None, instance=product)

    if form.is_valid() and request.method == "POST":
        # Simpan form dan kembali ke halaman awal
        form.save()
        return HttpResponseRedirect(reverse('main:show_main'))

    context = {'form': form}
    return render(request, "edit_product.html", context)

def delete_product(request, id):
    # Get data berdasarkan ID
    product = Product.objects.get(pk = id)
    # Hapus data
    product.delete()
    # Kembali ke halaman awal
    return HttpResponseRedirect(reverse('main:show_main'))

def get_product_json(request):
    product_item = Product.objects.all()
    return HttpResponse(serializers.serialize('json', product_item))

@csrf_exempt
def add_product_ajax(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        price = request.POST.get("price")
        description = request.POST.get("description")
        user = request.user

        new_product = Product(name=name, price=price, description=description, user=user)
        new_product.save()

        return HttpResponse(b"CREATED", status=201)

    return HttpResponseNotFound()

def play_song(request):
    song_data = {
        'title': 'Blinding Lights',
        'genres': ['Pop', 'Synthwave'],
        'artist': 'The Weeknd',
        'songwriters': ['Abel Tesfaye', 'Ahmad Balshe', 'Jason Quenneville', 'Max Martin', 'Oscar Holter'],
        'duration': 3.22,  
        'release_date': '29/11/2019',
        'year': 2019,
        'album': 'After Hours',
        'total_plays': 2_700_000_000,  
        'total_downloads': 1_000_000  
    }

    return render(request, 'play_song.html', {'song': song_data, 'user': request.user, 'user_is_premium': True})


@login_required
def play_user_playlist(request):
    songs_data = [
        {'id': 1, 'title': 'Shape of You', 'artist': 'Ed Sheeran', 'duration': '3 minutes 53 seconds', 'play_count': 0},
        {'id': 2, 'title': 'Blinding Lights', 'artist': 'The Weeknd', 'duration': '3 minutes 20 seconds', 'play_count': 0},
        {'id': 3, 'title': 'Rolling in the Deep', 'artist': 'Adele', 'duration': '3 minutes 48 seconds', 'play_count': 0},
        {'id': 4, 'title': 'Bad Guy', 'artist': 'Billie Eilish', 'duration': '3 minutes 14 seconds', 'play_count': 0},
        {'id': 5, 'title': 'Thriller', 'artist': 'Michael Jackson', 'duration': '5 minutes 57 seconds', 'play_count': 0}
    ]

    
    total_seconds = sum(int(song['duration'].split()[0]) * 60 + int(song['duration'].split()[2]) for song in songs_data)
    total_hours = total_seconds // 3600
    total_minutes = (total_seconds % 3600) // 60

    playlist_data = {
        'id': 101,
        'title': 'basdut',
        'creator': 'Lisan Al gaib',
        'songs': songs_data,
        'total_duration_hours': total_hours,
        'total_duration_minutes': total_minutes,
        'created_date': '2024-03-18',
        'description': 'A playlist featuring some of the biggest hits from various artists across genres.'
    }


    return render(request, 'play_user_playlist.html', {'playlist': playlist_data})

