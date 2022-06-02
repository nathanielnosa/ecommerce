from django.urls import path

from . import views 

urlpatterns=[
    path('register', views.register, name='register'),
    path('login', views.userLogin, name='login'),
    path('profile', views.userprofile, name='profile'),
    path('logout', views.logoutUser, name='logout'),
]