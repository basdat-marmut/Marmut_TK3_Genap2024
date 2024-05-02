from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField()
    city = models.CharField(max_length=100)
    is_artist = models.BooleanField(default=False)
    is_songwriter = models.BooleanField(default=False)
    is_podcaster = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class LabelProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
