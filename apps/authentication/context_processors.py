"""
Context processors for authentication app
"""

def user_preferences(request):
    """
    Add user preferences to the template context
    """
    print("=== CONTEXT PROCESSOR CALLED ===")
    
    context = {
        'user_theme': 'light',
        'user_high_contrast': False,
        'user_large_text': False,
        'user_reduce_motion': False,
        'user_language': 'en',
        'user_timezone': 'UTC',
        'user_date_format': 'MM/DD/YYYY',
        'user_time_format': '12',
    }
    
    if request.user.is_authenticated:
        print(f"User authenticated: {request.user.email}")
        try:
            # Get or create profile
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            print(f"Profile created: {created}")
            
            # Get preferences from notification_preferences field
            preferences = profile.notification_preferences or {}
            print(f"Preferences from DB: {preferences}")
            
            # Theme preferences
            context['user_theme'] = preferences.get('theme', 'light')
            context['user_high_contrast'] = preferences.get('high_contrast', False)
            context['user_large_text'] = preferences.get('large_text', False)
            context['user_reduce_motion'] = preferences.get('reduce_motion', False)
            
            # Language preferences from direct fields
            context['user_language'] = preferences.get('language', 'en')
            context['user_timezone'] = profile.timezone or 'UTC'
            context['user_date_format'] = preferences.get('date_format', 'MM/DD/YYYY')
            context['user_time_format'] = preferences.get('time_format', '12')
            
            # Availability (for therapists)
            if profile.user.user_type == 'therapist':
                context['user_availability'] = profile.availability_schedule or {}
                
            print(f"Final context: {context}")
                
        except Exception as e:
            # Log the error and use defaults
            print(f"Context processor error: {e}")
            import traceback
            traceback.print_exc()
            pass
    else:
        print("User not authenticated")
    
    print("=== CONTEXT PROCESSOR FINISHED ===")
    return context
