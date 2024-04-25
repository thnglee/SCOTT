import os

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse
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


def stream_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    song_path = settings.MEDIA_ROOT + song.get_uri()
    song_file = open(song_path, 'rb')

    response = StreamingHttpResponse(song_file, content_type='audio/mpeg')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(song_path))

    return response
