from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('profile-picture', views.handle_profile_picture, name='update-profile-picture'),
    path('people', views.find_people, name='find-people'),
    path('onboarding', views.onboarding, name='onboarding'),
    path('friends', views.friends, name='friends'),
    path('friends/invites', views.friend_invites, name='friend-invites'),
]
