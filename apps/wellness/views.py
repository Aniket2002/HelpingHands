from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .models import (
    MoodEntry, WellnessGoal, WellnessResource, WellnessActivity, 
    CrisisHotline, CrisisAlert, WellnessInsight
)

@login_required
def wellness_dashboard(request):
    """Enhanced wellness dashboard with analytics"""
    # Get recent mood entries for trends
    recent_moods = MoodEntry.objects.filter(user=request.user)[:7]
    
    # Calculate mood analytics
    last_30_days = timezone.now() - timedelta(days=30)
    mood_avg = MoodEntry.objects.filter(
        user=request.user, 
        created_at__gte=last_30_days
    ).aggregate(avg_mood=Avg('mood_rating'))['avg_mood'] or 0
    
    # Get wellness goals progress
    active_goals = WellnessGoal.objects.filter(user=request.user, is_completed=False)
    
    # Get recent insights
    insights = WellnessInsight.objects.filter(user=request.user, is_read=False)[:3]
    
    # Prepare mood chart data
    mood_chart_data = [
        {
            'date': entry.date.strftime('%Y-%m-%d'),
            'mood': entry.mood_rating,
            'energy': entry.energy_level,
            'stress': entry.stress_level,
            'score': entry.mood_score
        } for entry in reversed(recent_moods)
    ]
    
    context = {
        'recent_moods': recent_moods,
        'mood_average': round(mood_avg, 1),
        'active_goals': active_goals,
        'insights': insights,
        'mood_chart_data': json.dumps(mood_chart_data),
    }
    
    return render(request, 'wellness/dashboard.html', context)

@login_required
def mood_entries(request):
    """Enhanced mood tracking with detailed emotions and analytics"""
    if request.method == 'POST':
        # Create new mood entry
        mood_rating = request.POST.get('mood_rating')
        emotions = request.POST.getlist('emotions')
        energy_level = request.POST.get('energy_level')
        sleep_hours = request.POST.get('sleep_hours')
        stress_level = request.POST.get('stress_level')
        notes = request.POST.get('notes')
        triggers = request.POST.get('triggers')
        coping_strategies = request.POST.get('coping_strategies')
        
        try:
            MoodEntry.objects.create(
                user=request.user,
                mood_rating=int(mood_rating),
                emotions=emotions,
                energy_level=int(energy_level),
                sleep_hours=float(sleep_hours) if sleep_hours else None,
                stress_level=int(stress_level),
                notes=notes,
                triggers=triggers,
                coping_strategies=coping_strategies
            )
            messages.success(request, 'Mood entry saved successfully!')
            
            # Generate insights if conditions are met
            generate_mood_insights(request.user)
            
        except Exception as e:
            messages.error(request, f'Error saving mood entry: {str(e)}')
        
        return redirect('mood-entries')
    
    # Get mood history with pagination
    mood_history = MoodEntry.objects.filter(user=request.user)[:30]
    
    # Calculate analytics
    last_week = timezone.now() - timedelta(days=7)
    week_avg = MoodEntry.objects.filter(
        user=request.user,
        created_at__gte=last_week
    ).aggregate(avg_mood=Avg('mood_rating'))['avg_mood'] or 0
    
    context = {
        'mood_history': mood_history,
        'week_average': round(week_avg, 1),
        'emotion_choices': MoodEntry.EMOTION_CHOICES,
    }
    
    return render(request, 'wellness/mood_entries.html', context)

@login_required
def wellness_goals(request):
    """Enhanced goal tracking with progress analytics"""
    if request.method == 'POST':
        # Create new goal
        title = request.POST.get('title')
        description = request.POST.get('description')
        goal_type = request.POST.get('goal_type')
        target_value = request.POST.get('target_value')
        end_date = request.POST.get('end_date')
        
        try:
            WellnessGoal.objects.create(
                user=request.user,
                title=title,
                description=description,
                goal_type=goal_type,
                target_value=int(target_value),
                start_date=timezone.now().date(),
                end_date=datetime.strptime(end_date, '%Y-%m-%d').date()
            )
            messages.success(request, 'Goal created successfully!')
        except Exception as e:
            messages.error(request, f'Error creating goal: {str(e)}')
        
        return redirect('wellness-goals')
    
    active_goals = WellnessGoal.objects.filter(user=request.user, is_completed=False)
    completed_goals = WellnessGoal.objects.filter(user=request.user, is_completed=True)[:5]
    
    context = {
        'active_goals': active_goals,
        'completed_goals': completed_goals,
        'goal_types': WellnessGoal.GOAL_TYPES,
    }
    
    return render(request, 'wellness/goals.html', context)

@login_required
def wellness_resources(request):
    """Wellness library with guided content"""
    resource_type = request.GET.get('type', 'all')
    difficulty = request.GET.get('difficulty', 'all')
    
    resources = WellnessResource.objects.all()
    
    if resource_type != 'all':
        resources = resources.filter(resource_type=resource_type)
    
    if difficulty != 'all':
        resources = resources.filter(difficulty_level=difficulty)
    
    # Get user's completed activities
    completed_activities = WellnessActivity.objects.filter(
        user=request.user,
        completed_at__isnull=False
    ).values_list('resource_id', flat=True)
    
    context = {
        'resources': resources,
        'completed_activities': completed_activities,
        'resource_types': WellnessResource.RESOURCE_TYPES,
        'current_type': resource_type,
        'current_difficulty': difficulty,
    }
    
    return render(request, 'wellness/resources.html', context)

@login_required
def crisis_support(request):
    """24/7 Crisis support with hotlines and emergency contacts"""
    if request.method == 'POST':
        # Create crisis alert
        severity = request.POST.get('severity')
        message = request.POST.get('message')
        location = request.POST.get('location')
        
        CrisisAlert.objects.create(
            user=request.user,
            severity=severity,
            message=message,
            location=location
        )
        
        # Notify emergency contacts if high risk
        if severity in ['high', 'critical']:
            notify_emergency_contacts(request.user)
        
        messages.success(request, 'Crisis alert has been recorded. Help is on the way.')
        return redirect('crisis-support')
    
    # Get crisis hotlines by region
    hotlines = CrisisHotline.objects.filter(is_active=True)
    
    context = {
        'hotlines': hotlines,
        'severity_levels': CrisisAlert.SEVERITY_LEVELS,
    }
    
    return render(request, 'wellness/crisis_support.html', context)

@login_required
def mood_analytics_api(request):
    """API endpoint for mood analytics data"""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    mood_data = MoodEntry.objects.filter(
        user=request.user,
        created_at__gte=start_date
    ).values('date', 'mood_rating', 'energy_level', 'stress_level')
    
    analytics_data = {
        'mood_trend': list(mood_data),
        'averages': {
            'mood': MoodEntry.objects.filter(user=request.user, created_at__gte=start_date).aggregate(Avg('mood_rating'))['mood_rating__avg'] or 0,
            'energy': MoodEntry.objects.filter(user=request.user, created_at__gte=start_date).aggregate(Avg('energy_level'))['energy_level__avg'] or 0,
            'stress': MoodEntry.objects.filter(user=request.user, created_at__gte=start_date).aggregate(Avg('stress_level'))['stress_level__avg'] or 0,
        }
    }
    
    return JsonResponse(analytics_data)

def generate_mood_insights(user):
    """Generate personalized insights based on mood patterns"""
    # Get recent mood entries
    recent_entries = MoodEntry.objects.filter(user=user)[:14]
    
    if len(recent_entries) >= 7:
        # Calculate trend
        recent_avg = sum([entry.mood_rating for entry in recent_entries[:7]]) / 7
        previous_avg = sum([entry.mood_rating for entry in recent_entries[7:]]) / 7
        
        if recent_avg > previous_avg + 0.5:
            WellnessInsight.objects.create(
                user=user,
                insight_type='mood_trend',
                title='Positive Mood Trend Detected!',
                description=f'Your mood has improved by {recent_avg - previous_avg:.1f} points over the last week. Keep up the great work!',
                confidence_score=0.8
            )
        elif recent_avg < previous_avg - 0.5:
            WellnessInsight.objects.create(
                user=user,
                insight_type='mood_trend',
                title='Mood Decline Noticed',
                description=f'Your mood has decreased by {previous_avg - recent_avg:.1f} points. Consider reaching out for support.',
                confidence_score=0.8
            )

def notify_emergency_contacts(user):
    """Notify emergency contacts during crisis"""
    # This would integrate with SMS/email services
    # For now, we'll just log the action
    pass
