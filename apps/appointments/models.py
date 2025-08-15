from django.db import models
from apps.authentication.models import CustomUser

class TherapistProfile(models.Model):
    SPECIALIZATIONS = [
        ('anxiety', 'Anxiety Disorders'),
        ('depression', 'Depression'),
        ('trauma', 'Trauma & PTSD'),
        ('relationships', 'Relationship Counseling'),
        ('addiction', 'Addiction Recovery'),
        ('grief', 'Grief & Loss'),
        ('eating_disorders', 'Eating Disorders'),
        ('bipolar', 'Bipolar Disorder'),
        ('adhd', 'ADHD'),
        ('ocd', 'OCD'),
        ('family', 'Family Therapy'),
        ('couples', 'Couples Therapy'),
        ('child', 'Child Psychology'),
        ('adolescent', 'Adolescent Therapy'),
    ]
    
    THERAPY_APPROACHES = [
        ('cbt', 'Cognitive Behavioral Therapy'),
        ('dbt', 'Dialectical Behavior Therapy'),
        ('emdr', 'EMDR'),
        ('psychodynamic', 'Psychodynamic'),
        ('humanistic', 'Humanistic'),
        ('systemic', 'Systemic'),
        ('gestalt', 'Gestalt'),
        ('mindfulness', 'Mindfulness-Based'),
        ('somatic', 'Somatic Therapy'),
        ('art_therapy', 'Art Therapy'),
        ('music_therapy', 'Music Therapy'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='therapist_profile')
    license_number = models.CharField(max_length=100)
    specializations = models.JSONField(default=list)  # List of specialization codes
    therapy_approaches = models.JSONField(default=list)  # List of approach codes
    years_of_experience = models.IntegerField(default=0)
    education = models.TextField()
    bio = models.TextField()
    rate_per_session = models.DecimalField(max_digits=6, decimal_places=2)
    accepts_insurance = models.BooleanField(default=False)
    languages_spoken = models.JSONField(default=list)
    availability = models.JSONField(default=dict)  # Weekly availability schedule
    age_groups = models.JSONField(default=list)  # ['children', 'adolescents', 'adults', 'seniors']
    gender_preference = models.CharField(max_length=20, blank=True)  # Client preference
    is_accepting_clients = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dr. {self.user.full_name} - {', '.join(self.specializations[:2])}"
    
    def get_specializations_display(self):
        spec_dict = dict(self.SPECIALIZATIONS)
        return [spec_dict.get(spec, spec) for spec in self.specializations]
    
    def get_approaches_display(self):
        approach_dict = dict(self.THERAPY_APPROACHES)
        return [approach_dict.get(approach, approach) for approach in self.therapy_approaches]

class ClientPreferences(models.Model):
    URGENCY_LEVELS = [
        ('low', 'Not urgent, flexible timing'),
        ('medium', 'Would like to start within 2 weeks'),
        ('high', 'Need to start within a few days'),
        ('crisis', 'Need immediate support'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='client_preferences')
    concerns = models.JSONField(default=list)  # Primary mental health concerns
    preferred_specializations = models.JSONField(default=list)
    preferred_therapy_approaches = models.JSONField(default=list)
    therapist_gender_preference = models.CharField(max_length=20, blank=True)
    age_preference = models.CharField(max_length=50, blank=True)  # 'young', 'middle_aged', 'experienced'
    budget_max = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    insurance_provider = models.CharField(max_length=100, blank=True)
    preferred_languages = models.JSONField(default=list)
    session_frequency = models.CharField(max_length=50, default='weekly')
    preferred_times = models.JSONField(default=list)  # ['morning', 'afternoon', 'evening']
    urgency = models.CharField(max_length=20, choices=URGENCY_LEVELS, default='medium')
    previous_therapy_experience = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.full_name}'s Preferences"

class MatchingScore(models.Model):
    """Store and track matching scores between clients and therapists"""
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='matching_scores')
    therapist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='therapist_matches')
    overall_score = models.FloatField()
    specialization_score = models.FloatField(default=0.0)
    approach_score = models.FloatField(default=0.0)
    availability_score = models.FloatField(default=0.0)
    preference_score = models.FloatField(default=0.0)
    distance_score = models.FloatField(default=0.0)
    price_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['client', 'therapist']
    
    def __str__(self):
        return f"{self.client.full_name} -> {self.therapist.full_name}: {self.overall_score:.2f}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    client = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='client_appointments')
    therapist = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='therapist_appointments')
    appointment_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    session_url = models.URLField(blank=True)
    matching_score = models.ForeignKey(MatchingScore, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client.full_name} with {self.therapist.full_name} - {self.appointment_date}"
