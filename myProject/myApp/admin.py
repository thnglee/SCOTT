from django.contrib import admin
from .models import UserProfile, Song, Album, Playlist, Artist
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Song)
admin.site.register(Album)
admin.site.register(Playlist)
admin.site.register(Artist)
