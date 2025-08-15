from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def chat_rooms(request):
    return render(request, 'chat/rooms.html')

@login_required
def chat_room(request, room_id):
    return render(request, 'chat/room.html', {'room_id': room_id})

@login_required
def crisis_support(request):
    return render(request, 'chat/crisis_support.html')
