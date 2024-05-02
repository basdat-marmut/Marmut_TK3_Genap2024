from django import forms
from .models import Playlist, Song, UserPlaylist

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name', 'description']

class UserPlaylistForm(forms.ModelForm):
    song = forms.ModelChoiceField(queryset=Song.objects.all(), empty_label=None)

    class Meta:
        model = UserPlaylist
        fields = ['song']