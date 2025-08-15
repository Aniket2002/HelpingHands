from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.authentication.models import UserProfile, TherapistCredentials
from apps.professional.models import Therapist
from datetime import date, datetime, timedelta
from django.utils import timezone
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create demo users for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating demo users...'))
        
        # Create demo client user
        if not User.objects.filter(email='demo@mindbridge.com').exists():
            demo_client = User.objects.create_user(
                username='demo_client',
                email='demo@mindbridge.com',
                password='demo123456',
                first_name='Demo',
                last_name='Client',
                phone_number='+1234567890',
                date_of_birth=date(1990, 1, 1),
                user_type='client',
                emergency_contact_name='Emergency Contact',
                emergency_contact_phone='+1234567891'
            )
            
            # Create profile for demo client
            UserProfile.objects.create(
                user=demo_client,
                bio='Demo client account for testing the MindBridge platform.',
                timezone='America/New_York',
                language_preferences=['English'],
                notification_preferences={
                    'email_notifications': True,
                    'sms_notifications': False,
                    'appointment_reminders': True
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created demo client: {demo_client.email}')
            )
        
        # Create demo therapist user
        if not User.objects.filter(email='therapist@mindbridge.com').exists():
            demo_therapist = User.objects.create_user(
                username='demo_therapist',
                email='therapist@mindbridge.com',
                password='demo123456',
                first_name='Dr. Sarah',
                last_name='Johnson',
                phone_number='+1234567892',
                date_of_birth=date(1985, 5, 15),
                user_type='therapist'
            )
            
            # Create profile for demo therapist
            therapist_profile = UserProfile.objects.create(
                user=demo_therapist,
                bio='Licensed clinical psychologist with 10+ years of experience specializing in anxiety, depression, and trauma therapy. Passionate about helping clients achieve their mental health goals.',
                specialization='Clinical Psychology',
                experience_years=10,
                license_number='PSY123456',
                timezone='America/Los_Angeles',
                language_preferences=['English', 'Spanish'],
                hourly_rate=150.00,
                is_accepting_clients=True,
                availability_schedule={
                    'monday': ['09:00-17:00'],
                    'tuesday': ['09:00-17:00'],
                    'wednesday': ['09:00-17:00'],
                    'thursday': ['09:00-17:00'],
                    'friday': ['09:00-15:00'],
                    'saturday': [],
                    'sunday': []
                },
                notification_preferences={
                    'email_notifications': True,
                    'sms_notifications': True,
                    'appointment_reminders': True,
                    'new_client_notifications': True
                }
            )
            
            # Create therapist credentials
            TherapistCredentials.objects.create(
                user=demo_therapist,
                education='Ph.D. in Clinical Psychology - UCLA\nM.A. in Psychology - Stanford University',
                certifications=[
                    'Cognitive Behavioral Therapy Certification',
                    'Trauma-Informed Care Specialist',
                    'Mindfulness-Based Stress Reduction'
                ],
                verification_status='verified',
                verified_at=timezone.now()
            )
            
            # Create therapist in professional app
            therapist_obj = Therapist.objects.create(
                user=demo_therapist,
                license_number='PSY123456',
                specializations=['anxiety', 'depression', 'trauma', 'cognitive_behavioral'],
                therapy_types=['individual', 'couples', 'group'],
                bio='Licensed clinical psychologist with 10+ years of experience specializing in anxiety, depression, and trauma therapy.',
                years_experience=10,
                education='Ph.D. in Clinical Psychology - UCLA, M.A. in Psychology - Stanford University',
                certifications='Cognitive Behavioral Therapy Certification, Trauma-Informed Care Specialist, Mindfulness-Based Stress Reduction',
                hourly_rate=150.00,
                accepts_insurance=True,
                insurance_accepted=['Blue Cross Blue Shield', 'Aetna', 'Cigna', 'UnitedHealth'],
                languages_spoken=['English', 'Spanish'],
                availability_schedule={
                    'monday': ['09:00-17:00'],
                    'tuesday': ['09:00-17:00'],
                    'wednesday': ['09:00-17:00'],
                    'thursday': ['09:00-17:00'],
                    'friday': ['09:00-15:00'],
                    'saturday': [],
                    'sunday': []
                },
                is_accepting_patients=True,
                verified=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created demo therapist: {demo_therapist.email}')
            )
        
        # Create admin user
        if not User.objects.filter(email='admin@mindbridge.com').exists():
            admin_user = User.objects.create_superuser(
                username='mindbridge_admin',
                email='admin@mindbridge.com',
                password='admin123456',
                first_name='Admin',
                last_name='User'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created admin user: {admin_user.email}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n=== Demo Accounts Created ===')
        )
        self.stdout.write('Client Login:')
        self.stdout.write('  Email: demo@mindbridge.com')
        self.stdout.write('  Password: demo123456')
        self.stdout.write('')
        self.stdout.write('Therapist Login:')
        self.stdout.write('  Email: therapist@mindbridge.com') 
        self.stdout.write('  Password: demo123456')
        self.stdout.write('')
        self.stdout.write('Admin Login:')
        self.stdout.write('  Email: admin@mindbridge.com')
        self.stdout.write('  Password: admin123456')
        self.stdout.write(
            self.style.SUCCESS('Demo users setup complete!')
        )
