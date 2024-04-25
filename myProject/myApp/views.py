from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User

from myApp.models import UserProfile, Song, Artist, Album, Playlist


# Create your views here.
def home(request):
    songs = Song.objects.all()  # get all songs in the database
    return render(request, 'home.html', {'songs': songs})


def user_detail(request, username):
    user = User.objects.get(username=username)  # get the user object
    user_profile = UserProfile.objects.get(user=user)  # get the user profile object
    return render(request, 'user_detail.html', {'user': user, 'user_profile': user_profile})
