from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

from myApp.models import Song, Album, Playlist
from myApp.models import UserProfile


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    image_file = forms.ImageField(required=False)
    age = forms.IntegerField(required=False, validators=[MinValueValidator(0), MaxValueValidator(150)])
    sex = forms.ChoiceField(choices=UserProfile.SEX, initial="None")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "image_file", "age", "sex", "password1", "password2")


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class UpdateUserProfileForm(forms.ModelForm):
    image_file = forms.ImageField(required=False)
    become_artist = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'id': 'become_artist'}))
    artist_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'id': 'artist_name'}))

    def __init__(self, *args, **kwargs):
        super(UpdateUserProfileForm, self).__init__(*args, **kwargs)
        self.fields['age'].validators = [MinValueValidator(0), MaxValueValidator(150)]
        if hasattr(self.instance, 'artist'):
            self.fields['become_artist'].initial = True
            self.fields['artist_name'].initial = self.instance.artist.Artist_name

    class Meta:
        model = UserProfile
        fields = ['age', 'sex', 'image_file', 'become_artist', 'artist_name']


class UploadSongForm(forms.ModelForm):
    song_name = forms.CharField(max_length=100, required=True)
    song_file = forms.FileField(required=True)
    image_file = forms.ImageField(required=False)
    genres = forms.ChoiceField(choices=Song.GENRE)
    albums = forms.ModelMultipleChoiceField(queryset=Album.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile', None)
        super(UploadSongForm, self).__init__(*args, **kwargs)
        if profile and hasattr(profile, 'artist'):
            self.fields['albums'].queryset = Album.objects.filter(artist=profile.artist)

    class Meta:
        model = Song
        fields = ['song_name', 'song_file', 'image_file', 'genres', 'albums']


class UpdateSongForm(forms.ModelForm):
    song_file = forms.FileField(required=False)
    image_file = forms.ImageField(required=False)
    albums = forms.ModelMultipleChoiceField(queryset=Album.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
        super(UpdateSongForm, self).__init__(*args, **kwargs)
        if profile and hasattr(profile, 'artist'):
            self.fields['albums'].queryset = Album.objects.filter(artist=profile.artist)
        if self.instance:
            self.fields['albums'].initial = self.instance.albums.all()

    class Meta:
        model = Song
        fields = ['name', 'song_file', 'image_file', 'genres', 'albums']


class CreateAlbumForm(forms.ModelForm):
    album_name = forms.CharField(max_length=255)  # for album name
    image_file = forms.ImageField(required=False)  # for album cover image
    songs = forms.ModelMultipleChoiceField(queryset=Song.objects.all(), required=False)  # for selecting songs

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
        super(CreateAlbumForm, self).__init__(*args, **kwargs)
        if profile and hasattr(profile, 'artist'):
            self.fields['songs'].queryset = Song.objects.filter(artists=profile.artist)

    class Meta:
        model = Album
        fields = ['album_name', 'image_file', 'songs']


class UpdateAlbumForm(forms.ModelForm):
    songs = forms.ModelMultipleChoiceField(queryset=Song.objects.all(), required=False)
    image_file = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
        super(UpdateAlbumForm, self).__init__(*args, **kwargs)
        if profile and hasattr(profile, 'artist'):
            self.fields['songs'].queryset = Song.objects.filter(artists=profile.artist)
        if self.instance:
            self.fields['songs'].initial = self.instance.songs.all()

    class Meta:
        model = Album
        fields = ['name', 'image_file', 'songs']


class CreatePlaylistForm(forms.ModelForm):
    search_query = forms.CharField(max_length=255, required=False)
    songs = forms.ModelMultipleChoiceField(
        queryset=Song.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Playlist
        fields = ['name', 'songs']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        search_query = self.initial.get('search_query') or self.data.get('search_query')
        if search_query:
            self.fields['songs'].queryset = Song.objects.filter(name__icontains=search_query)
        else:
            self.fields['songs'].queryset = Song.objects.all()
