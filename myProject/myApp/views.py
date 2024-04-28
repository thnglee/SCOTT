import os
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.core.files.storage import default_storage
from django.http import StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from myApp.forms import SongForm, CustomUserCreationForm
from myApp.models import UserProfile, Song, Artist


# Create your views here.
class Login(LoginView):
    template_name = 'forms/authentication/login.html'
    next_page = 'home'


class Logout(LogoutView):
    next_page = 'home'


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            if 'image' in request.FILES:
                image = request.FILES['image']
                new_image_name = form.cleaned_data['username'] + os.path.splitext(image.name)[1]
                print(new_image_name)
                default_storage.save('image/user/' + new_image_name, image)
            else:
                new_image_name = 'default.png'
                print(new_image_name)

            user_profile = UserProfile(user=user,
                                       image_uri=new_image_name,
                                       age=form.cleaned_data['age'],
                                       sex=form.cleaned_data['sex'])
            user_profile.save()
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'forms/authentication/register.html', {'form': form})


def home(request):
    songs = Song.objects.all()  # get all songs in the database
    if request.user.is_authenticated:
        user = request.user  # get the username of the current user
        user_profile = UserProfile.objects.get(user=user)  # get the user profile object
        return render(request, 'home.html', {'songs': songs, 'user': user, 'user_profile': user_profile})
    else:
        return render(request, 'home.html', {'songs': songs})


def user_detail(request, username):
    user = User.objects.get(username=username)  # get the user object
    user_profile = UserProfile.objects.get(user=user)  # get the user profile object
    return render(request, 'templates/forms/user_detail.html', {'user': user, 'user_profile': user_profile})


@login_required(login_url='/login/')
def upload_song(request):
    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            user_profile = UserProfile.objects.get(user=request.user)
            artist = Artist.objects.get(user=user_profile)
            new_name = artist.Artist_name + "_" + clean_filename(form.cleaned_data['song_name'])

            # Name
            song.name = form.cleaned_data['song_name']

            # Image
            if 'image' in request.FILES:
                image = request.FILES['image']
                new_image_name = new_name + os.path.splitext(image.name)[1]
                default_storage.save('image/song/' + new_image_name, image)
            else:
                new_image_name = 'default.png'
            song.image_uri = new_image_name

            # Audio
            song_file = request.FILES['song_file']
            new_song_filename = new_name + os.path.splitext(song_file.name)[1]
            default_storage.save('audio/' + new_song_filename, song_file)
            song.uri = new_song_filename

            # Genre
            song.genres = form.cleaned_data['genres']

            # Save the song object
            song.save()

            # Album
            song.albums.add(form.cleaned_data['album'])

            # Artist
            song.artists.add(artist)

            form.save_m2m()  # save many-to-many data
            return redirect('home')
    else:
        form = SongForm()

    return render(request, 'forms/upload_song.html', {'form': form})


def stream_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    song_path = settings.MEDIA_ROOT + song.get_uri()
    song_file = open(song_path, 'rb')

    # Get the file extension
    _, file_extension = os.path.splitext(song_path)

    # Determine the content type based on the file extension
    if file_extension.lower() == '.mp3':
        content_type = 'audio/mpeg'
    elif file_extension.lower() == '.flac':
        content_type = 'audio/flac'
    else:
        content_type = 'application/octet-stream'  # Default content type

    response = StreamingHttpResponse(song_file, content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(song_path))

    return response


"""
def update_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    if request.method == 'POST':
        form = SongForm(request.POST, instance=song)
        if form.is_valid():
            form.save()
            return redirect('song_detail', song_id=song.id)
    else:
        form = SongForm(instance=song)

    return render(request, 'update_song.html', {'form': form})
"""


@require_POST
def delete_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    song.delete()
    return redirect('home')


def clean_filename(filename):
    # Define a regex pattern for the invalid characters
    invalid_chars_pattern = r'[\\/*?:"<>|]'
    # Replace the invalid characters with an empty string
    cleaned_filename = re.sub(invalid_chars_pattern, '', filename)
    return cleaned_filename
