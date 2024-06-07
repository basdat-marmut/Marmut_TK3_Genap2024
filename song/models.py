from django.db import models
from django.contrib.auth.models import User
import uuid

class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    songwriter = models.CharField(max_length=100)
    duration = models.IntegerField()
    release_date = models.DateField()
    year = models.IntegerField()
    total_play = models.IntegerField(default=0)
    total_download = models.IntegerField(default=0)
    album = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class AkunPlaySong(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class DownloadedSong(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
