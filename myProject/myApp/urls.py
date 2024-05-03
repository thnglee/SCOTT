from django.urls import path

from . import views
from .views import Login, Logout

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('user/<str:user_name>/profile/', views.user_profile, name='user_profile'),
    path('user/profile/update/', views.update_profile, name='update_profile'),
    path('user/delete/', views.delete_user, name='delete_user'),

    path('song/upload/', views.upload_song, name='upload_song'),
    path('song/<int:song_id>/stream/', views.stream_song, name='stream_song'),
    path('song/<int:song_id>/update/', views.update_song, name='update_song'),
    path('song/<int:song_id>/delete/', views.delete_song, name='delete_song'),

    path('artist/<str:artist_name>/profile/', views.artist_profile, name='artist_profile'),
    path('album/create/', views.create_album, name='create_album'),
]
