import json
import os

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.
class UserProfile(models.Model):
    SEX = {
        "M": "Male",
        "F": "Female",
        "N": "None",
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image_uri = models.CharField(max_length=255, default="default.png")
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)], null=True, blank=True)
    sex = models.CharField(max_length=1, choices=SEX, default="None")

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('user-detail', args=[str(self.id)])

    def get_image_uri(self):
        return "/media/image/user/" + self.image_uri


class Artist(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    Artist_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.Artist_name

    def get_absolute_url(self):
        return reverse('artist-detail', args=[str(self.id)])


class Song(models.Model):
    GENRE = {
        "POP": "Pop",
        "ROCK": "Rock",
        "COUNTRY": "Country",
        "RAP": "Rap",
        "JAZZ": "Jazz",
        "BLUES": "Blues",
        "RNB": "R&B",
        "HIPHOP": "Hip Hop",
        "EDM": "Electronic Dance Music",
        "CLASSICAL": "Classical",
        "REGGAE": "Reggae",
        "HEAVY_METAL": "Heavy Metal",
        "FOLK": "Folk",
        "SOUL": "Soul",
        "PUNK": "Punk",
        "ALTERNATIVE": "Alternative",
        "INDIE": "Indie",
        "OTHER": "Other",
    }

    name = models.CharField(max_length=100, unique=True)
    image_uri = models.CharField(max_length=255, default="default.png")
    uri = models.CharField(max_length=255, unique=True)
    genres = models.CharField(max_length=255, choices=GENRE, default="Other")
    artists = models.ManyToManyField('Artist', related_name='songs')
    albums = models.ManyToManyField('Album', related_name='songs', blank=True)
    playlists = models.ManyToManyField('Playlist', related_name='songs', blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    view_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('song-detail', args=[str(self.id)])

    def get_image_uri(self):
        return "/media/image/song/" + self.image_uri

    def get_uri(self):
        return "/audio/" + self.uri

    def inc_view_count(self):
        self.view_count += 1
        self.save()

    def get_artist_name(self):
        return self.artists.all()[0].Artist_name

    def get_artist(self):
        return self.artists.all()[0]

    def get_genre(self):
        return self.genres

    def get_mime_type(self):
        _, file_extension = os.path.splitext(self.uri)
        if file_extension.lower() == '.mp3':
            return 'audio/mpeg'
        elif file_extension.lower() == '.flac':
            return 'audio/flac'
        else:
            return 'application/octet-stream'


class Album(models.Model):
    name = models.CharField(max_length=255)
    image_uri = models.CharField(max_length=255, default="default.png")
    like_count = models.IntegerField(default=0)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('album-detail', args=[str(self.id)])

    def get_image_uri(self):
        return "/media/image/album/" + self.image_uri

    def get_view_count(self):
        return sum(song.view_count for song in self.songs.all())

    def get_song_info(self):
        song_info = []
        for song in self.songs.all():
            info = {
                'stream_url': reverse('stream_song', args=[str(song.id)]),
                'image_uri': song.get_image_uri(),
                'artist_name': song.get_artist_name(),
                'song_name': song.name,
                'id': song.id,
            }
            song_info.append(info)
        return json.dumps(song_info)


class Playlist(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('playlist-detail', args=[str(self.id)])

    def get_all_songs(self):
        return self.songs.all()

    def get_song_info(self):
        song_info = []
        for song in self.songs.all():
            info = {
                'stream_url': reverse('stream_song', args=[str(song.id)]),
                'image_uri': song.get_image_uri(),
                'artist_name': song.get_artist_name(),
                'song_name': song.name,
                'id': song.id,
            }
            song_info.append(info)
        return json.dumps(song_info)
