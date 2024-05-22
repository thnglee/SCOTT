# Create your tests here.
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from .models import UserProfile, Artist, Song, Album, Playlist


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user, image_uri="test.png", age=30, sex="M")

    def test_user_profile_creation(self):
        self.assertEqual(self.user_profile.user.username, 'testuser')
        self.assertEqual(self.user_profile.image_uri, "test.png")
        self.assertEqual(self.user_profile.age, 30)
        self.assertEqual(self.user_profile.sex, "M")

    def test_get_image_uri(self):
        self.assertEqual(self.user_profile.get_image_uri(), "/media/image/user/test.png")


class ArtistModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='artistuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.artist = Artist.objects.create(user=self.user_profile, Artist_name='Test Artist')

    def test_artist_creation(self):
        self.assertEqual(self.artist.Artist_name, 'Test Artist')
        self.assertEqual(self.artist.user, self.user_profile)


class SongModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='artistuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.artist = Artist.objects.create(user=self.user_profile, Artist_name='Test Artist')
        self.song = Song.objects.create(
            name='Test Song',
            image_uri='test_song.png',
            uri='test_song.mp3',
            genres='POP'
        )
        self.song.artists.add(self.artist)

    def test_song_creation(self):
        self.assertEqual(self.song.name, 'Test Song')
        self.assertEqual(self.song.image_uri, 'test_song.png')
        self.assertEqual(self.song.uri, 'test_song.mp3')
        self.assertEqual(self.song.genres, 'POP')
        self.assertIn(self.artist, self.song.artists.all())

    def test_get_image_uri(self):
        self.assertEqual(self.song.get_image_uri(), "/media/image/song/test_song.png")

    def test_get_uri(self):
        self.assertEqual(self.song.get_uri(), "/audio/test_song.mp3")


class AlbumModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='artistuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.artist = Artist.objects.create(user=self.user_profile, Artist_name='Test Artist')
        self.album = Album.objects.create(name='Test Album', artist=self.artist)

    def test_album_creation(self):
        self.assertEqual(self.album.name, 'Test Album')
        self.assertEqual(self.album.artist, self.artist)


class PlaylistModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='playlistuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.playlist = Playlist.objects.create(name='Test Playlist', user=self.user_profile)

    def test_playlist_creation(self):
        self.assertEqual(self.playlist.name, 'Test Playlist')
        self.assertEqual(self.playlist.user, self.user_profile)


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.artist = Artist.objects.create(user=self.user_profile, Artist_name='Test Artist')
        self.song = Song.objects.create(
            name='Test Song',
            image_uri='test_song.png',
            uri='test_song.mp3',
            genres='POP'
        )
        self.song.artists.add(self.artist)

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_user_profile_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_profile', args=['testuser']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/authentication/register.html')

    def test_upload_song_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('upload_song'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'song/upload.html')

    def test_song_info_view(self):
        response = self.client.get(reverse('song_info', args=[self.song.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'song/info.html')
