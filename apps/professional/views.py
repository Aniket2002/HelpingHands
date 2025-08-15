from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    Therapist, Appointment, TherapistReview, TherapyGoal, 
    TherapistAvailability, InsuranceProvider
)
from .forms import AppointmentForm, TherapistSearchForm, TherapyGoalForm, ReviewForm

@login_required
def therapist_search(request):
    """Search and filter therapists"""
    form = TherapistSearchForm(request.GET or None)
    therapists = Therapist.objects.filter(is_accepting_patients=True, verified=True)
    
    # Apply filters
    if form.is_valid():
        specialty = form.cleaned_data.get('specialty')
        therapy_type = form.cleaned_data.get('therapy_type')
        max_rate = form.cleaned_data.get('max_rate')
        insurance = form.cleaned_data.get('insurance')
        language = form.cleaned_data.get('language')
        
        if specialty:
            therapists = therapists.filter(specializations__contains=[specialty])
        
        if therapy_type:
            therapists = therapists.filter(therapy_types__contains=[therapy_type])
        
        if max_rate:
            therapists = therapists.filter(hourly_rate__lte=max_rate)
        
        if insurance:
            therapists = therapists.filter(accepts_insurance=True, insurance_accepted__contains=[insurance])
        
        if language:
            therapists = therapists.filter(languages_spoken__contains=[language])
    
    # Order by existing rating fields (simplified for now)
    therapists = therapists.order_by('-rating', '-total_reviews', 'hourly_rate')
    
    # Pagination
    paginator = Paginator(therapists, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'therapists': page_obj,
        'total_therapists': therapists.count(),
    }
    return render(request, 'professional/therapist_search.html', context)

@login_required
def therapist_detail(request, therapist_id):
    """Detailed therapist profile with booking option"""
    therapist = get_object_or_404(Therapist, id=therapist_id, verified=True)
    
    # Get reviews - for now, create empty list since models might not be migrated
    reviews = []  # Simplified to avoid model relation issues
    
    # For now, create some dummy available slots
    # In a real app, this would query the TherapistAvailability model
    available_slots = []
    today = timezone.now().date()
    
    # Generate some sample available slots for the next 7 days
    for day in range(7):
        check_date = today + timedelta(days=day)
        # Skip weekends for simplicity
        if check_date.weekday() < 5:  # Monday = 0, Friday = 4
            for hour in [9, 10, 14, 15, 16]:  # 9am, 10am, 2pm, 3pm, 4pm
                slot_datetime = timezone.make_aware(
                    datetime.combine(check_date, timezone.datetime.min.time().replace(hour=hour))
                )
                
                # Check if slot is not booked
                try:
                    is_booked = Appointment.objects.filter(
                        therapist=therapist,
                        date_time=slot_datetime,
                        status__in=['scheduled', 'confirmed']
                    ).exists()
                except:
                    is_booked = False
                
                if not is_booked:
                    available_slots.append({
                        'date': check_date,
                        'time': slot_datetime.time(),
                        'datetime': slot_datetime,
                    })
    
    try:
        user_has_appointment = Appointment.objects.filter(
            user=request.user,
            therapist=therapist,
            status__in=['scheduled', 'confirmed']
        ).exists()
    except:
        user_has_appointment = False
    
    context = {
        'therapist': therapist,
        'reviews': reviews,
        'available_slots': available_slots[:20],  # Show first 20 slots
        'user_has_appointment': user_has_appointment,
    }
    return render(request, 'professional/therapist_detail.html', context)

@login_required
@require_POST
def book_appointment(request, therapist_id):
    """Book an appointment with a therapist"""
    therapist = get_object_or_404(Therapist, id=therapist_id, verified=True)
    
    try:
        data = json.loads(request.body)
        appointment_datetime = timezone.datetime.fromisoformat(data['datetime'])
        session_type = data.get('session_type', 'therapy')
        notes = data.get('notes', '')
        
        # Check if slot is still available
        if Appointment.objects.filter(
            therapist=therapist,
            date_time=appointment_datetime,
            status__in=['scheduled', 'confirmed']
        ).exists():
            return JsonResponse({'error': 'Time slot no longer available'}, status=400)
        
        # Calculate cost
        duration = 50  # Default session duration
        if session_type == 'intake':
            duration = 90
            cost = float(therapist.hourly_rate) * 1.5
        else:
            cost = float(therapist.hourly_rate)
        
        # Create appointment
        appointment = Appointment.objects.create(
            user=request.user,
            therapist=therapist,
            date_time=appointment_datetime,
            duration_minutes=duration,
            session_type=session_type,
            notes_before=notes,
            cost=cost,
        )
        
        messages.success(request, f'Appointment booked with {therapist.full_name}!')
        return JsonResponse({'success': True, 'appointment_id': str(appointment.id)})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def appointment_list(request):
    """List user's appointments"""
    appointments = Appointment.objects.filter(user=request.user).select_related('therapist__user')
    
    # Separate upcoming and past appointments
    now = timezone.now()
    upcoming = appointments.filter(date_time__gte=now, status__in=['scheduled', 'confirmed'])
    past = appointments.filter(date_time__lt=now).exclude(status='cancelled')
    
    context = {
        'upcoming_appointments': upcoming,
        'past_appointments': past,
    }
    return render(request, 'professional/appointment_list.html', context)

@login_required
def appointment_detail(request, appointment_id):
    """Detailed appointment view"""
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        user=request.user
    )
    
    # Check if user can leave a review
    can_review = (
        appointment.status == 'completed' and
        not hasattr(appointment, 'therapistreview')
    )
    
    context = {
        'appointment': appointment,
        'can_review': can_review,
    }
    return render(request, 'professional/appointment_detail.html', context)

@login_required
@require_POST
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        user=request.user,
        status__in=['scheduled', 'confirmed']
    )
    
    # Check if cancellation is allowed (e.g., at least 24 hours before)
    if appointment.date_time <= timezone.now() + timedelta(hours=24):
        messages.error(request, 'Cannot cancel appointment less than 24 hours before scheduled time.')
        return redirect('appointment-detail', appointment_id=appointment_id)
    
    appointment.status = 'cancelled'
    appointment.save()
    
    messages.success(request, 'Appointment cancelled successfully.')
    return redirect('appointment-list')

@login_required
def therapy_goals(request):
    """Manage therapy goals"""
    if request.method == 'POST':
        form = TherapyGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'Therapy goal added successfully!')
            return redirect('therapy-goals')
    else:
        form = TherapyGoalForm()
    
    goals = TherapyGoal.objects.filter(user=request.user, is_active=True)
    completed_goals = TherapyGoal.objects.filter(
        user=request.user, 
        is_active=False, 
        progress_percentage=100
    )
    
    context = {
        'form': form,
        'goals': goals,
        'completed_goals': completed_goals,
    }
    return render(request, 'professional/therapy_goals.html', context)

@login_required
@require_POST
def update_goal_progress(request, goal_id):
    """Update therapy goal progress"""
    goal = get_object_or_404(TherapyGoal, id=goal_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        progress = int(data['progress'])
        
        if 0 <= progress <= 100:
            goal.progress_percentage = progress
            if progress == 100:
                goal.is_active = False
            goal.save()
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Invalid progress value'}, status=400)
            
    except (ValueError, KeyError):
        return JsonResponse({'error': 'Invalid data'}, status=400)

@login_required
def leave_review(request, appointment_id):
    """Leave a review for a therapist"""
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        user=request.user,
        status='completed'
    )
    
    # Check if review already exists
    if hasattr(appointment, 'therapistreview'):
        messages.info(request, 'You have already reviewed this appointment.')
        return redirect('appointment-detail', appointment_id=appointment_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.therapist = appointment.therapist
            review.appointment = appointment
            review.save()
            
            # Update therapist's overall rating - simplified for now
            therapist = appointment.therapist
            # Skip rating update until models are properly migrated
            # This would normally update therapist.rating and therapist.total_reviews
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('appointment-detail', appointment_id=appointment_id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'professional/leave_review.html', context)

@login_required
def professional_dashboard(request):
    """Dashboard for professional support features"""
    # Get user's recent appointments
    recent_appointments = Appointment.objects.filter(
        user=request.user
    ).select_related('therapist__user')[:5]
    
    # Get active therapy goals
    active_goals = TherapyGoal.objects.filter(
        user=request.user, 
        is_active=True
    )[:3]
    
    # Calculate stats
    total_sessions = Appointment.objects.filter(
        user=request.user, 
        status='completed'
    ).count()
    
    avg_goal_progress = active_goals.aggregate(
        avg_progress=Avg('progress_percentage')
    )['avg_progress'] or 0
    
    # Get recommended therapists
    recommended_therapists = Therapist.objects.filter(
        verified=True,
        is_accepting_patients=True
    ).order_by('-rating')[:3]
    
    context = {
        'recent_appointments': recent_appointments,
        'active_goals': active_goals,
        'total_sessions': total_sessions,
        'avg_goal_progress': round(avg_goal_progress),
        'recommended_therapists': recommended_therapists,
    }
    return render(request, 'professional/dashboard.html', context)
