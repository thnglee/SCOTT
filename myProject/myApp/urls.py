from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.urls import path

from . import views
from .views import Login, ChangePassword

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),

    path('user/<str:user_name>/profile/', views.user_profile, name='user_profile'),
    path('user/profile/update/', views.update_profile, name='update_profile'),
    path('user/profile/update/change_password/', ChangePassword.as_view(), name='change_password'),
    path('user/delete/', views.delete_user, name='delete_user'),

    path('password_reset/', PasswordResetView.as_view(
        template_name='user/authentication/password/password_reset/password_reset.html'), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='user/authentication/password/password_reset/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='user/authentication/password/password_reset/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='user/authentication/password/password_reset/password_reset_complete.html'),
         name='password_reset_complete'),

    path('song/upload/', views.upload_song, name='upload_song'),
    path('song/<int:song_id>/info/', views.song_info, name='song_info'),
    path('song/<int:song_id>/stream/', views.stream_song, name='stream_song'),
    path('song/<int:song_id>/update/', views.update_song, name='update_song'),
    path('song/<int:song_id>/delete/', views.delete_song, name='delete_song'),

    path('artist/<str:artist_name>/profile/', views.artist_profile, name='artist_profile'),
    path('artist/workspace/', views.artist_workspace, name='artist_workspace'),

    path('album/create/', views.create_album, name='create_album'),
    path('album/<str:album_name>/info/', views.album_info, name='album_info'),
    path('album/<int:album_id>/update/', views.update_album, name='update_album'),
    path('album/<int:album_id>/delete/', views.delete_album, name='delete_album'),

    path('playlist/create/', views.create_playlist, name='create_playlist'),
    path('playlist/<str:playlist_name>/info/', views.playlist_info, name='playlist_info'),
    path('playlist/<int:playlist_id>/delete/', views.delete_playlist, name='delete_playlist'),
]
