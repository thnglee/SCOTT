from django.contrib.auth.views import LoginView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='forms/login.html'), name='login'),
    path('user/<str:username>/', views.user_detail, name='user-detail'),
    path('upload_song/', views.upload_song, name='upload_song'),
    path('stream_song/<int:song_id>/', views.stream_song, name='stream-song'),
]
