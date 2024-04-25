from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('user/<str:username>/', views.user_detail, name='user-detail'),
]
