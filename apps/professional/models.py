from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class Therapist(models.Model):
    """Mental health professionals available on the platform"""
    SPECIALIZATION_CHOICES = [
        ('anxiety', 'Anxiety Disorders'),
        ('depression', 'Depression'),
        ('trauma', 'Trauma & PTSD'),
        ('addiction', 'Addiction Recovery'),
        ('relationships', 'Relationship Counseling'),
        ('grief', 'Grief & Loss'),
        ('eating_disorders', 'Eating Disorders'),
        ('bipolar', 'Bipolar Disorder'),
        ('ocd', 'OCD'),
        ('adhd', 'ADHD'),
        ('family_therapy', 'Family Therapy'),
        ('group_therapy', 'Group Therapy'),
        ('cognitive_behavioral', 'Cognitive Behavioral Therapy'),
        ('dialectical_behavioral', 'Dialectical Behavior Therapy'),
        ('mindfulness', 'Mindfulness-Based Therapy'),
    ]
    
    THERAPY_TYPE_CHOICES = [
        ('individual', 'Individual Therapy'),
        ('couples', 'Couples Therapy'),
        ('family', 'Family Therapy'),
        ('group', 'Group Therapy'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, unique=True)
    specializations = models.JSONField(default=list)  # List of specialization keys
    therapy_types = models.JSONField(default=list)  # List of therapy type keys
    bio = models.TextField(max_length=1000)
    years_experience = models.PositiveIntegerField()
    education = models.TextField(max_length=500)
    certifications = models.TextField(max_length=500, blank=True)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    accepts_insurance = models.BooleanField(default=False)
    insurance_accepted = models.JSONField(default=list, blank=True)
    languages_spoken = models.JSONField(default=list)
    availability_schedule = models.JSONField(default=dict)  # Weekly schedule
    is_accepting_patients = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'),
                                validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-rating', '-verified', 'user__first_name']
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return f"Dr. {self.user.get_full_name()}"
    
    @property
    def specialization_display(self):
        """Return human-readable specializations"""
        spec_dict = dict(self.SPECIALIZATION_CHOICES)
        return [spec_dict.get(spec, spec) for spec in self.specializations]
    
    @property
    def average_session_cost(self):
        """Calculate average cost based on therapy types"""
        base_rate = float(self.hourly_rate)
        if 'couples' in self.therapy_types or 'family' in self.therapy_types:
            return base_rate * 1.25  # 25% premium for couples/family
        return base_rate

class Appointment(models.Model):
    """Appointments between users and therapists"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    SESSION_TYPE_CHOICES = [
        ('intake', 'Initial Consultation'),
        ('therapy', 'Therapy Session'),
        ('followup', 'Follow-up'),
        ('crisis', 'Crisis Intervention'),
        ('group', 'Group Session'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_appointments')
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name='therapist_appointments')
    date_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=50)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='therapy')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes_before = models.TextField(max_length=500, blank=True, help_text="What would you like to discuss?")
    notes_after = models.TextField(max_length=1000, blank=True, help_text="Session notes (therapist only)")
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    paid = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True, help_text="Video call link")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_time']
        unique_together = ['therapist', 'date_time']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.therapist.full_name} - {self.date_time}"

class TherapistReview(models.Model):
    """Reviews and ratings for therapists"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name='reviews')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(max_length=1000, blank=True)
    communication_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    effectiveness_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    would_recommend = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'therapist']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.therapist.full_name} by {self.user.get_full_name()}"

class TherapyGoal(models.Model):
    """Therapy goals set by users"""
    GOAL_CATEGORY_CHOICES = [
        ('anxiety', 'Manage Anxiety'),
        ('depression', 'Overcome Depression'),
        ('relationships', 'Improve Relationships'),
        ('self_esteem', 'Build Self-Esteem'),
        ('stress', 'Reduce Stress'),
        ('trauma', 'Process Trauma'),
        ('communication', 'Better Communication'),
        ('coping', 'Develop Coping Skills'),
        ('lifestyle', 'Lifestyle Changes'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='therapy_goals')
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name='client_goals', null=True, blank=True)
    category = models.CharField(max_length=20, choices=GOAL_CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    target_date = models.DateField(null=True, blank=True)
    progress_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()}: {self.title}"

class TherapistAvailability(models.Model):
    """Available time slots for therapists"""
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name='availability_slots')
    weekday = models.PositiveIntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['therapist', 'weekday', 'start_time']
        ordering = ['weekday', 'start_time']
    
    def __str__(self):
        weekday_choices = {
            0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
            4: 'Friday', 5: 'Saturday', 6: 'Sunday'
        }
        weekday_name = weekday_choices.get(self.weekday, 'Unknown')
        return f"{self.therapist.user.first_name} {self.therapist.user.last_name} - {weekday_name} {self.start_time}-{self.end_time}"

class InsuranceProvider(models.Model):
    """Insurance providers accepted by therapists"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
