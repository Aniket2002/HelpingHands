from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('client', 'Client'),
        ('therapist', 'Therapist'),
        ('psychiatrist', 'Psychiatrist'),
        ('counselor', 'Counselor'),
        ('volunteer', 'Volunteer'),
    )
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='client')
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')],
        blank=True
    )
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'auth_user'
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def profile_picture_url(self):
        """Safely get profile picture URL or default"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            try:
                return self.profile_picture.url
            except (ValueError, AttributeError):
                return '/static/default-avatar.svg'
        return '/static/default-avatar.svg'

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    specialization = models.CharField(max_length=100, blank=True)  # For therapists
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language_preferences = models.JSONField(default=list)
    availability_schedule = models.JSONField(default=dict)  # Weekly schedule
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    is_accepting_clients = models.BooleanField(default=True)
    notification_preferences = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.user.full_name}'s Profile"

class TherapistCredentials(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='credentials')
    education = models.TextField()
    certifications = models.JSONField(default=list)
    verification_documents = models.FileField(upload_to='credentials/', blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    verified_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_therapists'
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.full_name} - {self.verification_status}"
