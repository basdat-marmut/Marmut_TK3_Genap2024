from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('playlist/', include('playlist.urls')),
    path('langganan/', include('langganan.urls', namespace='langganan')),
    path('song/', include('song.urls')),
    path('royalty_management/', include('royalty_management.urls')),
]
