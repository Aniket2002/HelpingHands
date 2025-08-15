from django.db import models
from apps.authentication.models import CustomUser

class MoodEntry(models.Model):
    MOOD_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Fair'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mood_entries')
    mood_rating = models.IntegerField(choices=MOOD_CHOICES)
    notes = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'date']
    
    def __str__(self):
        mood_display = dict(self.MOOD_CHOICES).get(self.mood_rating, str(self.mood_rating))
        return f"{self.user.full_name} - {mood_display} ({self.date})"

class WellnessGoal(models.Model):
    GOAL_TYPES = [
        ('mood', 'Mood Improvement'),
        ('exercise', 'Physical Exercise'),
        ('meditation', 'Meditation'),
        ('sleep', 'Sleep Quality'),
        ('social', 'Social Connection'),
        ('habit', 'Habit Building'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wellness_goals')
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    target_value = models.IntegerField(help_text="Target number (e.g., 30 minutes, 5 times)")
    current_progress = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return min(100, (self.current_progress / self.target_value) * 100)
    
    def __str__(self):
        return f"{self.user.full_name} - {self.title}"

class JournalEntry(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='journal_entries')
    title = models.CharField(max_length=200)
    content = models.TextField()
    mood_before = models.IntegerField(choices=MoodEntry.MOOD_CHOICES, blank=True, null=True)
    mood_after = models.IntegerField(choices=MoodEntry.MOOD_CHOICES, blank=True, null=True)
    is_private = models.BooleanField(default=True)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.title}"

class WellnessResource(models.Model):
    RESOURCE_TYPES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('audio', 'Audio/Podcast'),
        ('exercise', 'Exercise'),
        ('meditation', 'Meditation'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    content_url = models.URLField(blank=True)
    content_file = models.FileField(upload_to='wellness_resources/', blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    difficulty_level = models.CharField(
        max_length=20,
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        default='beginner'
    )
    tags = models.JSONField(default=list)
    is_featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return self.title

class WellnessActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wellness_activities')
    resource = models.ForeignKey(WellnessResource, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    rating = models.IntegerField(
        choices=[(i, f'{i} stars') for i in range(1, 6)],
        blank=True, 
        null=True,
        help_text="Rate from 1-5 stars"
    )
    notes = models.TextField(blank=True)
    
    @property
    def is_completed(self):
        return self.completed_at is not None
    
    def __str__(self):
        return f"{self.user.full_name} - {self.resource.title}"
