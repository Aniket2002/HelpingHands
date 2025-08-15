from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_rooms, name='chat-rooms'),
    path('room/<uuid:room_id>/', views.chat_room, name='chat-room'),
    path('crisis/', views.crisis_support, name='crisis-support'),
]
