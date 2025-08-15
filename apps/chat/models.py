from django.db import models
from apps.authentication.models import CustomUser
import uuid

class ChatRoom(models.Model):
    ROOM_TYPES = [
        ('private', 'Private Chat'),
        ('group', 'Group Chat'),
        ('support', 'Support Group'),
        ('crisis', 'Crisis Intervention'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='private')
    participants = models.ManyToManyField(CustomUser, related_name='chat_rooms')
    moderators = models.ManyToManyField(CustomUser, related_name='moderated_rooms', blank=True)
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=50)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('voice', 'Voice Note'),
        ('system', 'System Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField(blank=True)
    file_attachment = models.FileField(upload_to='chat_files/', blank=True, null=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.full_name}: {self.content[:50]}..."

class MessageReaction(models.Model):
    REACTION_TYPES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😂'),
        ('sad', '😢'),
        ('angry', '😠'),
        ('support', '🤗'),
    ]
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user', 'reaction_type']
    
    def __str__(self):
        reaction_display = dict(self.REACTION_TYPES).get(self.reaction_type, self.reaction_type)
        return f"{self.user.full_name} {reaction_display} on {self.message.id}"

class CrisisAlert(models.Model):
    ALERT_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical - Immediate Response'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='crisis_alerts')
    alert_level = models.CharField(max_length=20, choices=ALERT_LEVELS)
    message = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    emergency_contact_notified = models.BooleanField(default=False)
    responder = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='responded_alerts'
    )
    is_resolved = models.BooleanField(default=False)
    response_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Crisis Alert - {self.user.full_name} ({self.alert_level})"
