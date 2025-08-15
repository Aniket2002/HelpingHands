from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser, UserProfile, TherapistCredentials
from .forms import ClientRegistrationForm, TherapistRegistrationForm

def home_view(request):
    """Modern landing page"""
    return render(request, 'home.html')

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')
        
        if email_or_username and password:
            # Try to authenticate with email first
            user = authenticate(request, username=email_or_username, password=password)
            
            # If email authentication fails, try to find user by email and authenticate with username
            if not user:
                try:
                    user_obj = CustomUser.objects.get(email=email_or_username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    pass
            
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email/username or password')
        else:
            messages.error(request, 'Please provide both email/username and password')
    
    return render(request, 'auth/login.html')

def register_view(request):
    """General registration view - shows user type selection"""
    return render(request, 'auth/register_selection.html')

def client_register_view(request):
    """Client registration view"""
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Welcome to MindBridge. You can now log in and start your mental health journey.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'auth/client_register.html', {'form': form})

def therapist_register_view(request):
    """Therapist registration view"""
    if request.method == 'POST':
        form = TherapistRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration submitted! Your therapist profile is pending verification. You will receive an email once approved.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = TherapistRegistrationForm()
    
    return render(request, 'auth/therapist_register.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard_view(request):
    """User dashboard"""
    context = {
        'user': request.user,
        'recent_sessions': [],  # TODO: Implement
        'upcoming_appointments': [],  # TODO: Implement
    }
    return render(request, 'dashboard.html', context)

@login_required
def profile_view(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'auth/profile.html', {'profile': profile})

@login_required
def settings_view(request):
    """User settings view"""
    return render(request, 'auth/settings.html', {'user': request.user})

@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password changed successfully. Please log in again.')
            return redirect('login')
    
    return render(request, 'auth/change_password.html')

@login_required
def email_preferences_view(request):
    """Email preferences view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        notifications = profile.notification_preferences or {}
        notifications.update({
            'email_notifications': request.POST.get('email_notifications') == 'on',
            'appointment_reminders': request.POST.get('appointment_reminders') == 'on',
            'newsletter': request.POST.get('newsletter') == 'on',
            'security_alerts': request.POST.get('security_alerts') == 'on',
        })
        profile.notification_preferences = notifications
        profile.save()
        messages.success(request, 'Email preferences updated successfully.')
    
    return render(request, 'auth/email_preferences.html', {'profile': profile})

@login_required
def privacy_settings_view(request):
    """Privacy settings view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle privacy settings updates
        notifications = profile.notification_preferences or {}
        notifications.update({
            'profile_visibility': request.POST.get('profile_visibility', 'private'),
            'allow_contact': request.POST.get('allow_contact') == 'on',
            'data_sharing': request.POST.get('data_sharing') == 'on',
        })
        profile.notification_preferences = notifications
        profile.save()
        messages.success(request, 'Privacy settings updated successfully.')
    
    return render(request, 'auth/privacy_settings.html', {'profile': profile})

@login_required
def notification_settings_view(request):
    """Notification settings view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        notifications = profile.notification_preferences or {}
        notifications.update({
            'email_notifications': request.POST.get('email_notifications') == 'on',
            'sms_notifications': request.POST.get('sms_notifications') == 'on',
            'push_notifications': request.POST.get('push_notifications') == 'on',
            'appointment_reminders': request.POST.get('appointment_reminders') == 'on',
            'therapy_insights': request.POST.get('therapy_insights') == 'on',
            'community_updates': request.POST.get('community_updates') == 'on',
        })
        profile.notification_preferences = notifications
        profile.save()
        messages.success(request, 'Notification settings updated successfully.')
    
    return render(request, 'auth/notification_settings.html', {'profile': profile})

@login_required
def download_data_view(request):
    """Download user data view"""
    return render(request, 'auth/download_data.html')

@login_required
def availability_settings_view(request):
    """Availability settings view (for therapists)"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        schedule = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            if request.POST.get(f'{day}_enabled'):
                start_time = request.POST.get(f'{day}_start')
                end_time = request.POST.get(f'{day}_end')
                if start_time and end_time:
                    schedule[day] = [f'{start_time}-{end_time}']
                else:
                    schedule[day] = []
            else:
                schedule[day] = []
        
        profile.availability_schedule = schedule
        profile.save()
        messages.success(request, 'Availability updated successfully.')
        return redirect('availability_settings')
    
    # Pass days context for template
    days_context = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'), 
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ]
    
    # Prepare schedule data for template
    schedule_data = {}
    if hasattr(profile, 'availability_schedule') and profile.availability_schedule:
        for day, day_name in days_context:
            if day in profile.availability_schedule and profile.availability_schedule[day]:
                time_range = profile.availability_schedule[day][0]  # "09:00-17:00"
                if '-' in time_range:
                    start_time, end_time = time_range.split('-')
                    schedule_data[day] = {
                        'enabled': True,
                        'start_time': start_time,
                        'end_time': end_time
                    }
                else:
                    schedule_data[day] = {'enabled': False, 'start_time': '09:00', 'end_time': '17:00'}
            else:
                schedule_data[day] = {'enabled': False, 'start_time': '09:00', 'end_time': '17:00'}
    else:
        for day, day_name in days_context:
            schedule_data[day] = {'enabled': False, 'start_time': '09:00', 'end_time': '17:00'}
    
    return render(request, 'auth/availability_settings.html', {
        'profile': profile,
        'days': days_context,
        'schedule_data': schedule_data
    })

@login_required
def theme_preferences_view(request):
    """Theme preferences view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        notifications = profile.notification_preferences or {}
        
        # Debug: print what we're receiving
        print(f"POST data: {dict(request.POST)}")
        print(f"Current notifications: {notifications}")
        
        notifications.update({
            'theme': request.POST.get('theme', 'light'),
            'reduce_motion': request.POST.get('reduce_motion') == 'on',
            'high_contrast': request.POST.get('high_contrast') == 'on',
            'large_text': request.POST.get('large_text') == 'on',
        })
        
        print(f"Updated notifications: {notifications}")
        
        profile.notification_preferences = notifications
        profile.save()
        
        # Debug: verify it was saved
        profile.refresh_from_db()
        print(f"Saved notifications: {profile.notification_preferences}")
        
        messages.success(request, 'Theme preferences updated successfully.')
        return redirect('theme_preferences')
    
    return render(request, 'auth/theme_preferences.html', {'profile': profile})

@login_required
def language_settings_view(request):
    """Language and region settings view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update basic language and timezone
        profile.timezone = request.POST.get('timezone', 'UTC')
        profile.language_preferences = [request.POST.get('language', 'English')]
        
        # Update regional preferences
        notifications = profile.notification_preferences or {}
        notifications.update({
            'date_format': request.POST.get('date_format', 'MM/DD/YYYY'),
            'time_format': request.POST.get('time_format', '12'),
            'first_day_of_week': request.POST.get('first_day_of_week', 'sunday'),
        })
        profile.notification_preferences = notifications
        profile.save()
        messages.success(request, 'Language and region settings updated successfully.')
        return redirect('language_settings')
    
    return render(request, 'auth/language_settings.html', {'profile': profile})
