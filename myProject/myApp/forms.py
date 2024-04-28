from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

from myApp.models import Song, Album
from myApp.models import UserProfile


class SongForm(forms.ModelForm):
    song_name = forms.CharField(max_length=100)  # for song name
    song_file = forms.FileField()  # for song file upload
    image = forms.ImageField(required=False)  # for picture upload
    genres = forms.ChoiceField(choices=Song.GENRE)  # for selecting a genre
    album = forms.ModelChoiceField(queryset=Album.objects.all())  # for selecting an album

    class Meta:
        model = Song
        fields = ['song_name', 'song_file', 'image', 'album', 'genres']


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    image = forms.ImageField(required=False)
    age = forms.IntegerField(required=False, validators=[MinValueValidator(0), MaxValueValidator(150)])
    sex = forms.ChoiceField(choices=UserProfile.SEX, initial="None")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "image", "age", "sex", "password1", "password2")

