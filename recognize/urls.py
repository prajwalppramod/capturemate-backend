from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('recognize', views.recognize, name='recognize'),
    path('photo', views.photo, name='photo'),
    path('send', views.send_photo, name='send_photo'),
    path('photos', views.photos, name='photos'),
    path('chat', views.get_chat, name='chat_photos'),
]