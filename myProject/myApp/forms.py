from django import forms
from myApp.models import Song

from django import forms
from myApp.models import Song, Album


class SongForm(forms.ModelForm):
    song_name = forms.CharField(max_length=100)  # for song name
    song_file = forms.FileField()  # for song file upload
    image = forms.ImageField()  # for picture upload
    genres = forms.ChoiceField(choices=Song.GENRE)  # for selecting a genre
    album = forms.ModelChoiceField(queryset=Album.objects.all())  # for selecting an album

    class Meta:
        model = Song
        fields = ['song_name', 'song_file', 'image', 'album', 'genres']
