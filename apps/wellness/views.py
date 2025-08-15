from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def wellness_dashboard(request):
    return render(request, 'wellness/dashboard.html')

@login_required
def mood_entries(request):
    return render(request, 'wellness/mood_entries.html')

@login_required
def wellness_goals(request):
    return render(request, 'wellness/goals.html')

@login_required
def wellness_resources(request):
    return render(request, 'wellness/resources.html')
