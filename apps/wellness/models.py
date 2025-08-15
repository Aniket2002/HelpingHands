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
    
    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('anxious', 'Anxious'),
        ('calm', 'Calm'),
        ('stressed', 'Stressed'),
        ('excited', 'Excited'),
        ('angry', 'Angry'),
        ('peaceful', 'Peaceful'),
        ('overwhelmed', 'Overwhelmed'),
        ('hopeful', 'Hopeful'),
        ('lonely', 'Lonely'),
        ('grateful', 'Grateful'),
    ]
    
    ENERGY_CHOICES = [
        (1, 'Very Low Energy'),
        (2, 'Low Energy'),
        (3, 'Moderate Energy'),
        (4, 'High Energy'),
        (5, 'Very High Energy')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mood_entries')
    mood_rating = models.IntegerField(choices=MOOD_CHOICES)
    emotions = models.JSONField(default=list, help_text="List of emotions felt")
    energy_level = models.IntegerField(choices=ENERGY_CHOICES, default=3)
    sleep_hours = models.FloatField(null=True, blank=True, help_text="Hours of sleep last night")
    stress_level = models.IntegerField(choices=MOOD_CHOICES, default=3, help_text="Stress level (1-5)")
    notes = models.TextField(blank=True)
    triggers = models.TextField(blank=True, help_text="What triggered these feelings?")
    coping_strategies = models.TextField(blank=True, help_text="What helped or might help?")
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'date']
    
    def __str__(self):
        mood_display = dict(self.MOOD_CHOICES).get(self.mood_rating, str(self.mood_rating))
        return f"{self.user.full_name} - {mood_display} ({self.date})"
    
    @property
    def mood_score(self):
        """Calculate overall mood score including energy and stress"""
        return round((self.mood_rating + self.energy_level + (6 - self.stress_level)) / 3, 1)

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


class CrisisHotline(models.Model):
    REGIONS = [
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('UK', 'United Kingdom'),
        ('AU', 'Australia'),
        ('INTL', 'International'),
    ]
    
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    text_number = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField()
    region = models.CharField(max_length=4, choices=REGIONS)
    available_24_7 = models.BooleanField(default=True)
    languages = models.JSONField(default=list, help_text="Languages supported")
    specialties = models.JSONField(default=list, help_text="Special focus areas")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['region', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.region})"


class CrisisAlert(models.Model):
    SEVERITY_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wellness_crisis_alerts')
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    message = models.TextField()
    mood_triggers = models.JSONField(default=list)
    location = models.CharField(max_length=200, blank=True)
    emergency_contact_notified = models.BooleanField(default=False)
    professional_contacted = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Crisis Alert - {self.user.full_name} ({self.severity})"


class PrivacyLog(models.Model):
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('data_access', 'Data Access'),
        ('data_export', 'Data Export'),
        ('data_delete', 'Data Deletion'),
        ('profile_update', 'Profile Update'),
        ('mood_entry', 'Mood Entry Created'),
        ('appointment_book', 'Appointment Booked'),
        ('crisis_alert', 'Crisis Alert Triggered'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='privacy_logs')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.action} ({self.timestamp})"


class WellnessInsight(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wellness_insights')
    insight_type = models.CharField(max_length=50, choices=[
        ('mood_trend', 'Mood Trend Analysis'),
        ('sleep_pattern', 'Sleep Pattern'),
        ('stress_trigger', 'Stress Trigger Identification'),
        ('progress_milestone', 'Progress Milestone'),
        ('recommendation', 'Personalized Recommendation'),
    ])
    title = models.CharField(max_length=200)
    description = models.TextField()
    data_points = models.JSONField(default=dict, help_text="Supporting data for the insight")
    confidence_score = models.FloatField(default=0.0, help_text="AI confidence in insight (0-1)")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.title}"
