from django import forms
from .models import Album, Song

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'label']

class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'duration']

