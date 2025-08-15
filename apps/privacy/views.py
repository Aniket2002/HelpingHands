from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def privacy_dashboard(request):
    """Main privacy and security dashboard"""
    return render(request, 'privacy/privacy_security.html')

@login_required
def privacy_settings(request):
    """Manage privacy settings"""
    if request.method == 'POST':
        # Handle privacy settings update
        messages.success(request, 'Privacy settings updated successfully!')
        return redirect('privacy:dashboard')
    return render(request, 'privacy/settings.html')

@login_required
def request_data_export(request):
    """Request data export (GDPR/HIPAA)"""
    if request.method == 'POST':
        # Handle data export request
        messages.success(request, 'Data export request submitted. You will receive an email when ready.')
        return redirect('privacy:dashboard')
    return render(request, 'privacy/data_export.html')

@login_required
def request_data_deletion(request):
    """Request data deletion (Right to be forgotten)"""
    if request.method == 'POST':
        # Handle data deletion request
        messages.warning(request, 'Data deletion request submitted for review.')
        return redirect('privacy:dashboard')
    return render(request, 'privacy/data_deletion.html')

@login_required
def access_log(request):
    """Show user's data access log"""
    return render(request, 'privacy/access_log.html')

@login_required
def security_incidents(request):
    """Show security incidents affecting the user"""
    return render(request, 'privacy/security_incidents.html')
