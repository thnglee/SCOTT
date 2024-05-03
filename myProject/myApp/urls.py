from django.urls import path

from . import views
from .views import Login, Logout

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('user/<int:user_id>/', views.update_user_info, name='update_user_info'),
    path('delete_user/', views.delete_user, name='delete_user'),

    path('upload_song/', views.upload_song, name='upload_song'),
    path('stream_song/<int:song_id>/', views.stream_song, name='stream_song'),
    path('update_song/<int:song_id>/', views.update_song, name='update_song'),
    path('delete_song/<int:song_id>/', views.delete_song, name='delete_song'),

    path('artist/<int:artist_id>/', views.artist_page, name='artist_page'),
    path('create_album/', views.create_album, name='create_album'),
]
