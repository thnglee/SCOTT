import os
import random
import re

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import Http404, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from pydub import AudioSegment

from myApp.forms import (CreateUserForm, UploadSongForm, UpdateSongForm, UpdateUserForm,
                         UpdateUserProfileForm, CreateAlbumForm, CreatePlaylistForm, UpdateAlbumForm)
from myApp.models import Song, UserProfile, Artist, Album, Playlist


# Create your views here.
class Login(LoginView):
    template_name = 'templates/user/authentication/login.html'
    next_page = 'home'


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('home')


class ChangePassword(PasswordChangeView):
    success_url = reverse_lazy('login')
    template_name = 'user/authentication/password/change_password.html'

    def form_valid(self, form):
        logout(self.request)
        return super().form_valid(form)


def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            if 'image_file' in request.FILES:
                image = request.FILES['image_file']
                new_image_name = form.cleaned_data['username'] + os.path.splitext(image.name)[1]
                default_storage.save('image/user/' + new_image_name, image)
            else:
                new_image_name = 'default.png'

            profile = UserProfile(user=user,
                                  image_uri=new_image_name,
                                  age=form.cleaned_data['age'],
                                  sex=form.cleaned_data['sex'])
            profile.save()
            form.save()
            return redirect('login')
    else:
        form = CreateUserForm()
    return render(request, 'user/authentication/register.html', {'form': form})


def user_profile(request, user_name):
    try:
        user = get_object_or_404(User, username=user_name)
    except Http404:
        return redirect('home')

    profile = UserProfile.objects.get(user=user)
    current_user = request.user
    return render(request,
                  'user/profile.html',
                  {'user': user, 'profile': profile, 'current_user': current_user})


@login_required(login_url='/login/')
def update_profile(request):
    user = request.user
    current_user = user
    profile = UserProfile.objects.get(user=user)
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=user)
        user_profile_form = UpdateUserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form.save()
            profile = user_profile_form.save(commit=False)

            # Image
            if 'image_file' in request.FILES:
                # Delete the old image file
                if profile.image_uri != 'default.png':
                    default_storage.delete('image/user/' + profile.image_uri)

                image = request.FILES['image_file']
                new_image_name = profile.user.username + os.path.splitext(image.name)[1]
                default_storage.save('image/user/' + new_image_name, image)
                profile.image_uri = new_image_name

            # Artist
            if user_profile_form.cleaned_data.get('become_artist'):
                if hasattr(profile, 'artist'):
                    if profile.artist.Artist_name != user_profile_form.cleaned_data.get('artist_name'):
                        for song in Song.objects.filter(artists=profile.artist):
                            new_name = user_profile_form.cleaned_data.get('artist_name') + "_" + song.name
                            rename_file(song, new_name)
                        for album in Album.objects.filter(artist=profile.artist):
                            new_name = user_profile_form.cleaned_data.get('artist_name') + "_" + album.name
                            rename_file_album(album, new_name)
                        profile.artist.Artist_name = user_profile_form.cleaned_data.get('artist_name')
                else:
                    if '' != user_profile_form.cleaned_data.get('artist_name'):
                        Artist.objects.create(user=profile,
                                              Artist_name=user_profile_form.cleaned_data.get('artist_name'))
                    else:
                        Artist.objects.create(user=profile, Artist_name=user_form.cleaned_data.get('username'))
                profile.artist.save()
            else:
                if hasattr(profile, 'artist'):
                    artist = profile.artist

                    songs = Song.objects.filter(artists=artist)
                    for song in songs:
                        if song.uri:
                            default_storage.delete('audio/' + song.uri)
                        if song.image_uri != 'default.png':
                            default_storage.delete('image/song/' + song.image_uri)
                    songs.delete()

                    albums = Album.objects.filter(artist=artist)
                    for album in albums:
                        if album.image_uri != 'default.png':
                            default_storage.delete('image/album/' + album.image_uri)
                    albums.delete()

                    artist.delete()

            profile.save()

            return render(request,
                          'user/profile.html',
                          {'user': user, 'profile': profile, 'current_user': current_user})
    else:
        user_form = UpdateUserForm(instance=request.user)
        user_profile_form = UpdateUserProfileForm(instance=profile)

    return render(request, 'user/update_profile.html',
                  {'user_form': user_form, 'profile_form': user_profile_form, 'current_user': current_user})


@login_required(login_url='/login/')
def delete_user(request):
    user = get_object_or_404(User, username=request.user.username)
    profile = UserProfile.objects.get(user=user)

    songs = Song.objects.filter(artists__user=profile)
    albums = Album.objects.filter(artist__user=profile)

    # Delete song files and images
    for song in songs:
        if song.uri:
            default_storage.delete('audio/' + song.uri)
        if song.image_uri != 'default.png':
            default_storage.delete('image/song/' + song.image_uri)
        song.delete()

    # Delete album images
    for album in albums:
        if album.image_uri != 'default.png':
            default_storage.delete('image/album/' + album.image_uri)

    # Delete user image
    if profile.image_uri != 'default.png':
        default_storage.delete('image/user/' + profile.image_uri)
    user.delete()

    return redirect('home')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'user/authentication/password/password_reset/password_reset.html'
    email_template_name = 'user/authentication/password/password_reset/password_reset_email.html'
    subject_template_name = 'user/authentication/password/password_reset/password_reset_subject.txt'
    success_url = '/password_reset/done/'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'user/authentication/password/password_reset/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'user/authentication/password/password_reset/password_reset_confirm.html'
    success_url = '/reset/done/'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'user/authentication/password/password_reset/password_reset_complete.html'


def home(request):
    songs = Song.objects.all()
    num_songs = min(12, len(songs))
    random_songs = random.sample(list(songs), num_songs)
    artists = Artist.objects.all()
    query = request.GET.get('q', '')
    songs_query = search_song(query) if query else Song.objects.none()
    context = {
        'songs': random_songs,
        'artists': artists,
        'songs_query': songs_query,
    }
    if request.user.is_authenticated:
        user = request.user
        current_user = user
        profile = UserProfile.objects.get(user=user)
        playlists = Playlist.objects.filter(user=profile)
        context.update({'user': user, 'profile': profile, 'playlists': playlists, 'current_user': current_user})
        return render(request, 'home.html', context)
    else:
        return render(request, 'home.html', context)


def compress_audio(input_path, output_path, target_bitrate="320k"):
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, bitrate=target_bitrate)


@login_required(login_url='/login/')
def upload_song(request):
    profile = UserProfile.objects.get(user=request.user)
    if not hasattr(profile, 'artist'):
        return redirect('update_profile')
    if request.method == 'POST':
        form = UploadSongForm(request.POST, request.FILES, profile=profile)
        if form.is_valid():
            song = form.save(commit=False)
            profile = UserProfile.objects.get(user=request.user)
            artist = Artist.objects.get(user=profile)
            new_name = artist.Artist_name + "_" + clean_filename(form.cleaned_data['song_name'])

            # Name
            song.name = form.cleaned_data['song_name']

            # Image
            if 'image_file' in request.FILES:
                image = request.FILES['image_file']
                new_image_name = new_name + os.path.splitext(image.name)[1]
                default_storage.save('image/song/' + new_image_name, image)
            else:
                new_image_name = 'default.png'
            song.image_uri = new_image_name

            # Audio
            song_file = request.FILES['song_file']
            new_song_filename = new_name + os.path.splitext(song_file.name)[1]
            temp_path = 'audio/temp/' + new_song_filename
            final_path = 'audio/' + new_song_filename
            save = default_storage.save(temp_path, song_file)
            if save:
                compress_audio('media/' + temp_path, 'media/' + final_path)
                default_storage.delete(temp_path)
            song.uri = new_song_filename

            # Genre
            song.genres = form.cleaned_data['genres']

            # Save the song object
            song.save()

            # Album
            if 'albums' in form.changed_data:
                song.albums.set(form.cleaned_data['albums'])

            # Artist
            song.artists.add(artist)

            form.save_m2m()  # save many-to-many data
            return render(request, 'user/artist/workspace.html',
                          {'artist': artist, 'songs': artist.songs, 'albums': artist.album_set,
                           'current_user': request.user})
    else:
        form = UploadSongForm(profile=profile)

    return render(request, 'song/upload.html', {'form': form, 'current_user': request.user})


def song_info(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    return render(request, 'song/info.html', {'song': song, 'current_user': request.user})


def stream_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    song_path = settings.MEDIA_ROOT + song.get_uri()

    # Get the file extension
    _, file_extension = os.path.splitext(song_path)

    # Determine the content type based on the file extension
    if file_extension.lower() == '.mp3':
        content_type = 'audio/mpeg'
    elif file_extension.lower() == '.flac':
        content_type = 'audio/flac'
    else:
        content_type = 'application/octet-stream'  # Default content type

    response = FileResponse(open(song_path, 'rb'), content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(song_path))
    response["Accept-Ranges"] = "bytes"
    return response


def update_song(request, song_id):
    try:
        song = get_object_or_404(Song, id=song_id)
    except Http404:
        return redirect('home')
    profile = UserProfile.objects.get(user=request.user)
    if not song.artists.filter(user=profile).exists():
        return redirect('home')

    if request.method == 'POST':
        form = UpdateSongForm(request.POST, request.FILES, profile=profile, instance=song)
        if form.is_valid():
            song = form.save(commit=False)

            artist = Artist.objects.get(user=profile)
            new_name = artist.Artist_name + "_" + clean_filename(form.cleaned_data['name'])

            # Name
            if 'name' in form.changed_data:
                song.name = form.cleaned_data['name']
                rename_file(song, new_name)

            # Audio
            if 'song_file' in request.FILES:
                if song.uri:
                    default_storage.delete('audio/' + song.uri)
                file = request.FILES['song_file']
                new_song_filename = new_name + os.path.splitext(file.name)[1]
                final_path = 'audio/' + new_song_filename
                temp_path = 'audio/temp/' + new_song_filename
                save = default_storage.save(temp_path, file)
                if save:
                    compress_audio('media/' + temp_path, 'media/' + final_path)
                    default_storage.delete(temp_path)
                song.uri = new_song_filename

            # Image
            if 'image_file' in request.FILES:
                # Delete the old image file
                if song.image_uri != 'default.png':
                    default_storage.delete('image/song/' + song.image_uri)

                image = request.FILES['image_file']
                new_image_name = new_name + os.path.splitext(image.name)[1]
                default_storage.save('image/song/' + new_image_name, image)
                song.image_uri = new_image_name

            # Genre
            if 'genres' in form.changed_data:
                song.genres = form.cleaned_data['genres']

            song.save()

            # Album
            if 'albums' in form.changed_data:
                song.albums.set(form.cleaned_data['albums'])

            form.save_m2m()
            return render(request, 'user/artist/workspace.html',
                          {'artist': artist, 'songs': artist.songs, 'albums': artist.album_set,
                           'current_user': request.user})
    else:
        form = UpdateSongForm(instance=song, profile=profile)

    return render(request, 'song/update.html', {'form': form, 'current_user': request.user})


@require_POST
def delete_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    current_user = request.user
    profile = UserProfile.objects.get(user=current_user)
    songs = Song.objects.filter(artists=profile.artist)
    albums = Album.objects.filter(artist=profile.artist)
    # Delete the song file and image file
    if song.uri:
        default_storage.delete('audio/' + song.uri)

    if song.image_uri != 'default.png':
        default_storage.delete('image/song/' + song.image_uri)
    song.delete()
    return render(request, 'user/artist/workspace.html',
                  {'artist': profile.artist, 'songs': songs, 'albums': albums,
                   'current_user': request.user})


def artist_profile(request, artist_name):
    current_user = request.user
    artist = Artist.objects.get(Artist_name=artist_name)
    profile = UserProfile.objects.get(user=artist.user.user)
    songs = Song.objects.filter(artists=artist)
    albums = Album.objects.filter(artist=artist)

    return render(request, 'user/artist/profile.html',
                  {'artist': artist, 'songs': songs, 'albums': albums, 'current_user': current_user,
                   'profile': profile})


@login_required(login_url='/login/')
def artist_workspace(request):
    artist = Artist.objects.get(Artist_name=request.user.userprofile.artist.Artist_name)
    songs = Song.objects.filter(artists=artist)
    albums = Album.objects.filter(artist=artist)
    current_user = request.user

    return render(request, 'user/artist/workspace.html',
                  {'artist': artist, 'songs': songs, 'albums': albums, 'current_user': current_user})


@login_required(login_url='/login/')
def create_album(request):
    profile = UserProfile.objects.get(user=request.user)
    if not hasattr(profile, 'artist'):
        return redirect('update_profile')

    if request.method == 'POST':
        form = CreateAlbumForm(request.POST, request.FILES, profile=profile)
        if form.is_valid():
            album = form.save(commit=False)
            album.artist = profile.artist

            # Name
            album.name = form.cleaned_data['album_name']

            # Image
            if 'image_file' in request.FILES:
                image = request.FILES['image_file']
                new_image_name = (album.artist.Artist_name + "_"
                                  + clean_filename(form.cleaned_data['album_name'])
                                  + os.path.splitext(image.name)[1])
                default_storage.save('image/album/' + new_image_name, image)
                album.image_uri = new_image_name
            else:
                album.image_uri = 'default.png'

            album.save()
            form.save_m2m()
            return redirect('home')
    else:
        form = CreateAlbumForm(profile=profile)

    return render(request, 'album/create.html', {'form': form})


def album_info(request, album_name):
    album = get_object_or_404(Album, name=album_name)
    return render(request, 'album/info.html', {'album': album})


@login_required(login_url='/login/')
def update_album(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    if request.method == 'POST':
        form = UpdateAlbumForm(request.POST, request.FILES, instance=album, profile=request.user.userprofile)
        if form.is_valid():
            album = form.save(commit=False)
            if 'name' in form.changed_data:
                album.name = form.cleaned_data['name']
                new_name = album.artist.Artist_name + "_" + form.cleaned_data['name']
                rename_file_album(album, new_name)

            if 'image_file' in request.FILES:
                if album.image_uri != 'default.png':
                    default_storage.delete('image/album/' + album.image_uri)
                image = request.FILES['image_file']
                new_image_name = form.cleaned_data['name'] + "_" + os.path.splitext(image.name)[1]
                default_storage.save('image/album/' + new_image_name, image)
                album.image_uri = new_image_name

            album.save()

            if 'songs' in form.changed_data:
                album.songs.set(form.cleaned_data['songs'])
            form.save_m2m()

            return redirect('artist_workspace')

    else:
        form = UpdateAlbumForm(instance=album, profile=request.user.userprofile)
    return render(request, 'album/update.html', {'form': form})


@login_required(login_url='/login/')
def delete_album(request, album_id):
    album = get_object_or_404(Album, id=album_id)

    if album.image_uri != 'default.png':
        default_storage.delete('image/album/' + album.image_uri)
    album.delete()
    return redirect('home')


@login_required(login_url='/login/')
def create_playlist(request):
    search_query = request.GET.get('search_query', '')
    if request.method == 'POST':
        form = CreatePlaylistForm(request.POST, initial={'search_query': search_query})
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = UserProfile.objects.get(user=request.user)
            playlist.save()
            for song in form.cleaned_data['songs']:
                playlist.songs.add(song)

            form.save_m2m()
            return redirect('home')
    else:
        form = CreatePlaylistForm(initial={'search_query': search_query})

    return render(request, 'playlist/create.html', {'form': form})


@login_required(login_url='/login/')
def playlist_info(request, playlist_name):
    profile = UserProfile.objects.get(user=request.user)
    playlist = get_object_or_404(Playlist, name=playlist_name, user=profile)
    return render(request, 'playlist/info.html', {'playlist': playlist})


@login_required(login_url='/login/')
def delete_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    playlist.delete()
    return redirect('home')


def clean_filename(filename):
    invalid_chars_pattern = r'[\\/*?:"<>|]'

    cleaned_filename = re.sub(invalid_chars_pattern, '', filename)
    return cleaned_filename


def search_song(query):
    return Song.objects.filter(Q(name__icontains=query))


def rename_file(song, new_name):
    if song.uri:
        with default_storage.open('audio/' + song.uri, 'rb') as song_file:
            new_song_filename = new_name + os.path.splitext(song_file.name)[1]
            save = default_storage.save('audio/' + new_song_filename, song_file)
        if save:
            default_storage.delete('audio/' + song.uri)
        song.uri = new_song_filename

    if song.image_uri != 'default.png':
        with default_storage.open('image/song/' + song.image_uri, 'rb') as image:
            new_image_name = new_name + os.path.splitext(image.name)[1]
            save = default_storage.save('image/song/' + new_image_name, image)
        if save:
            default_storage.delete('image/song/' + song.image_uri)
        song.image_uri = new_image_name
    song.save()


def rename_file_album(album, new_name):
    if album.image_uri != 'default.png':
        with default_storage.open('image/album/' + album.image_uri, 'rb') as image:
            new_image_name = new_name + os.path.splitext(image.name)[1]
            save = default_storage.save('image/album/' + new_image_name, image)
        if save:
            default_storage.delete('image/album/' + album.image_uri)
        album.image_uri = new_image_name
    album.save()
