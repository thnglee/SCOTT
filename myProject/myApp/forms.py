from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

from myApp.models import Song, Album
from myApp.models import UserProfile


class SongInfo(forms.ModelForm):
    song_name = forms.CharField(max_length=100)  # for song name
    song_file = forms.FileField()  # for song file upload
    image_file = forms.ImageField(required=False)  # for picture upload
    genres = forms.ChoiceField(choices=Song.GENRE)  # for selecting a genre
    album = forms.ModelChoiceField(queryset=Album.objects.all(), required=False)  # for selecting an album

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SongInfo, self).__init__(*args, **kwargs)
        if user:
            self.fields['album'].queryset = Album.objects.filter(artist__user__user=user)

    class Meta:
        model = Song
        fields = ['song_name', 'song_file', 'image_file', 'album', 'genres']


class SongInfoUpdate(forms.ModelForm):
    song_file = forms.FileField(required=False)  # for song file upload
    image_file = forms.ImageField(required=False)  # for picture upload

    class Meta:
        model = Song
        fields = ['name', 'song_file', 'image_file', 'genres', 'albums']


class UserInfo(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    image_file = forms.ImageField(required=False)
    age = forms.IntegerField(required=False, validators=[MinValueValidator(0), MaxValueValidator(150)])
    sex = forms.ChoiceField(choices=UserProfile.SEX, initial="None")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "image_file", "age", "sex", "password1", "password2")


class UserInfoUpdate(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', ]


class UserProfileInfoUpdate(forms.ModelForm):
    image_file = forms.ImageField(required=False)
    become_artist = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'id': 'become_artist'}))
    artist_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'id': 'artist_name'}))

    def __init__(self, *args, **kwargs):
        super(UserProfileInfoUpdate, self).__init__(*args, **kwargs)
        if hasattr(self.instance, 'artist'):
            self.fields['become_artist'].initial = True
            self.fields['artist_name'].initial = self.instance.artist.Artist_name

    class Meta:
        model = UserProfile
        fields = ['age', 'sex', 'image_file', 'become_artist', 'artist_name']
