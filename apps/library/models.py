from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
import uuid

User = get_user_model()

class ResourceCategory(models.Model):
    """Categories for wellness resources"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500)
    icon = models.CharField(max_length=50, default='📚')  # Emoji or icon class
    color = models.CharField(max_length=7, default='#6366f1')  # Hex color
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Resource Categories'
    
    def __str__(self):
        return self.name

class WellnessResource(models.Model):
    """Mental health and wellness resources"""
    RESOURCE_TYPES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('audio', 'Audio/Podcast'),
        ('exercise', 'Exercise/Worksheet'),
        ('meditation', 'Guided Meditation'),
        ('tool', 'Interactive Tool'),
        ('course', 'Online Course'),
        ('book', 'Book Recommendation'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=1000)
    content = models.TextField(help_text="Main content of the resource")
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name='resources')
    tags = models.JSONField(default=list, help_text="List of tags for filtering")
    
    # Media fields
    thumbnail = models.URLField(blank=True, help_text="Thumbnail image URL")
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    audio_url = models.URLField(blank=True, help_text="Audio file or streaming URL")
    file_attachment = models.URLField(blank=True, help_text="PDF or other downloadable file")
    external_link = models.URLField(blank=True, help_text="External resource link")
    
    # Metadata
    author = models.CharField(max_length=200, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in minutes")
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='beginner')
    reading_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Engagement
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-is_featured', '-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('library:resource-detail', kwargs={'slug': self.slug})
    
    @property
    def estimated_time(self):
        """Return estimated time for consumption"""
        if self.duration_minutes:
            return f"{self.duration_minutes} min"
        elif self.reading_time_minutes:
            return f"{self.reading_time_minutes} min read"
        return "Quick read"

class UserProgress(models.Model):
    """Track user progress through resources"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(WellnessResource, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.PositiveIntegerField(default=0)
    bookmarked = models.BooleanField(default=False)
    liked = models.BooleanField(default=False)
    notes = models.TextField(max_length=1000, blank=True)
    
    class Meta:
        unique_together = ['user', 'resource']
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.resource.title}"
    
    @property
    def is_completed(self):
        return self.completed_at is not None

class WellnessPlan(models.Model):
    """Curated wellness plans with multiple resources"""
    PLAN_TYPES = [
        ('daily', 'Daily Practice'),
        ('weekly', 'Weekly Program'),
        ('challenge', '30-Day Challenge'),
        ('course', 'Learning Course'),
        ('crisis', 'Crisis Support'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=1000)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    resources = models.ManyToManyField(WellnessResource, through='PlanResource')
    estimated_duration_days = models.PositiveIntegerField()
    difficulty_level = models.CharField(max_length=20, choices=WellnessResource.DIFFICULTY_LEVELS)
    # Engagement
    enrollment_count = models.PositiveIntegerField(default=0)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    is_featured = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('library:plan-detail', kwargs={'slug': self.slug})

class PlanResource(models.Model):
    """Through model for wellness plans and resources"""
    plan = models.ForeignKey(WellnessPlan, on_delete=models.CASCADE)
    resource = models.ForeignKey(WellnessResource, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    is_required = models.BooleanField(default=True)
    unlock_after_days = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['plan', 'resource']

class PlanEnrollment(models.Model):
    """User enrollment in wellness plans"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(WellnessPlan, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    current_day = models.PositiveIntegerField(default=1)
    progress_percentage = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'plan']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.plan.title}"

class ResourceReview(models.Model):
    """User reviews for resources"""
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(WellnessResource, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    review_text = models.TextField(max_length=1000, blank=True)
    helpfulness_votes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'resource']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user.get_full_name()} for {self.resource.title}"

class StudyGroup(models.Model):
    """Study groups for wellness resources and plans"""
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    plan = models.ForeignKey(WellnessPlan, on_delete=models.CASCADE, related_name='study_groups')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='library_moderated_groups')
    members = models.ManyToManyField(User, related_name='study_groups')
    max_members = models.PositiveIntegerField(default=20)
    start_date = models.DateField()
    is_private = models.BooleanField(default=False)
    join_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
