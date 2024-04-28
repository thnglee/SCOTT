from django.urls import path

from . import views
from .views import Login, Logout

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('user/<str:username>/', views.user_detail, name='user-detail'),
    path('upload_song/', views.upload_song, name='upload_song'),
    path('stream_song/<int:song_id>/', views.stream_song, name='stream-song'),
]
