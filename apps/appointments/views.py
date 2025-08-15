from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import TherapistProfile, ClientPreferences, MatchingScore
from .matching_service import TherapistMatchingService

@login_required
def appointments_list(request):
    return render(request, 'appointments/list.html')

@login_required
def book_appointment(request):
    return render(request, 'appointments/book.html')

@login_required
def appointment_detail(request, appointment_id):
    return render(request, 'appointments/detail.html', {'appointment_id': appointment_id})

@login_required
def find_matches(request):
    """Find therapist matches for the current user"""
    matching_service = TherapistMatchingService()
    matches = matching_service.find_matches(request.user, limit=10)
    
    context = {
        'matches': matches,
        'has_preferences': hasattr(request.user, 'client_preferences')
    }
    return render(request, 'appointments/matches.html', context)

@login_required
def setup_preferences(request):
    """Setup or update client preferences for matching"""
    try:
        preferences = ClientPreferences.objects.get(user=request.user)
    except ClientPreferences.DoesNotExist:
        preferences = None
    
    if request.method == 'POST':
        # Process form data and save preferences
        data = request.POST
        
        if preferences:
            # Update existing preferences
            preferences.concerns = data.getlist('concerns')
            preferences.preferred_specializations = data.getlist('specializations')
            preferences.preferred_therapy_approaches = data.getlist('approaches')
            preferences.therapist_gender_preference = data.get('gender_preference', '')
            preferences.budget_max = data.get('budget_max') or None
            preferences.insurance_provider = data.get('insurance_provider', '')
            preferences.preferred_languages = data.getlist('languages')
            preferences.session_frequency = data.get('session_frequency', 'weekly')
            preferences.preferred_times = data.getlist('preferred_times')
            preferences.urgency = data.get('urgency', 'medium')
            preferences.previous_therapy_experience = data.get('previous_experience') == 'yes'
            preferences.save()
        else:
            # Create new preferences
            preferences = ClientPreferences.objects.create(
                user=request.user,
                concerns=data.getlist('concerns'),
                preferred_specializations=data.getlist('specializations'),
                preferred_therapy_approaches=data.getlist('approaches'),
                therapist_gender_preference=data.get('gender_preference', ''),
                budget_max=data.get('budget_max') or None,
                insurance_provider=data.get('insurance_provider', ''),
                preferred_languages=data.getlist('languages'),
                session_frequency=data.get('session_frequency', 'weekly'),
                preferred_times=data.getlist('preferred_times'),
                urgency=data.get('urgency', 'medium'),
                previous_therapy_experience=data.get('previous_experience') == 'yes'
            )
        
        messages.success(request, 'Your preferences have been saved! Let\'s find your matches.')
        return redirect('find-matches')
    
    # Get choices for form
    context = {
        'preferences': preferences,
        'specializations': TherapistProfile.SPECIALIZATIONS,
        'therapy_approaches': TherapistProfile.THERAPY_APPROACHES,
        'urgency_levels': ClientPreferences.URGENCY_LEVELS,
    }
    return render(request, 'appointments/preferences.html', context)

@login_required
def therapist_detail(request, therapist_id):
    """View therapist profile and matching details"""
    try:
        therapist_profile = TherapistProfile.objects.get(user__id=therapist_id)
        
        # Get matching score if available
        matching_score = None
        try:
            matching_score = MatchingScore.objects.get(
                client=request.user,
                therapist=therapist_profile.user
            )
        except MatchingScore.DoesNotExist:
            pass
        
        context = {
            'therapist': therapist_profile,
            'matching_score': matching_score,
        }
        return render(request, 'appointments/therapist_detail.html', context)
    except TherapistProfile.DoesNotExist:
        messages.error(request, 'Therapist not found.')
        return redirect('find-matches')
