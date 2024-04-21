from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
'''class User(models.Model):
    name = models.CharField(max_length=16, primary_key=True)
    password = models.CharField(max_length=26, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    firstname = models.CharField(max_length=10)
    lastname = models.CharField(max_length=10)
    image_uri = models.CharField(max_length=255)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])
    sex = models.CharField(max_length=5)'''


class UserProfile(models.Model):
    SEX = {
        "M": "Male",
        "F": "Female",
        "N": "None",
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image_uri = models.CharField(max_length=255)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)], null=True, blank=True)
    sex = models.CharField(max_length=1, choices=SEX)


class Artist(UserProfile):
    Artist_name = models.CharField(max_length=100, unique=True)


class Song(models.Model):
    name = models.CharField(max_length=100)
    image_uri = models.CharField(max_length=255)
    uri = models.CharField(max_length=255, unique=True)
    like_count = models.IntegerField()
    albums = models.ManyToManyField('Album', related_name='songs')
    playlists = models.ManyToManyField('Playlist', related_name='songs')


class Album(models.Model):
    name = models.CharField(max_length=255)
    image_uri = models.CharField(max_length=255)
    like_count = models.IntegerField()
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)


class Playlist(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
