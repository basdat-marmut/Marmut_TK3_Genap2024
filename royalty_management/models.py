from django.db import models
    
class Album(models.Model):
    title = models.CharField(max_length=100)
    label = models.ForeignKey('Label', on_delete=models.CASCADE, related_name='albums')
    release_date = models.DateField()
    artists = models.ManyToManyField('Artist', related_name='albums')

    def __str__(self):
        return self.title

# Refer to Album using a string in the ForeignKey definition
class Song(models.Model):
    title = models.CharField(max_length=100)
    album = models.ForeignKey('Album', on_delete=models.CASCADE, related_name='songs')
    duration = models.IntegerField(help_text='Duration in seconds')
    total_plays = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    artists = models.ManyToManyField('Artist', related_name='songs')
    songwriters = models.ManyToManyField('Songwriter', related_name='songs')

    def __str__(self):
        return self.title
    
class Songwriter(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
# Define other related models such as Artist and Label here
class Artist(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Label(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)
    contact_info = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Royalty(models.Model):
    artists = models.ForeignKey(Artist, on_delete=models.CASCADE)
    total_royalty = models.DecimalField(max_digits=10, decimal_places=2)