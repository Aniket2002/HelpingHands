from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def wellness_library(request):
    """Main wellness library page"""
    return render(request, 'library/wellness_library.html')

@login_required
def category_list(request):
    """List all resource categories"""
    return render(request, 'library/categories.html')

@login_required
def category_detail(request, category_slug):
    """Show resources in a specific category"""
    return render(request, 'library/category_detail.html')

@login_required
def resource_detail(request, slug):
    """Show detailed resource view"""
    return render(request, 'library/resource_detail.html')

@login_required
def plan_list(request):
    """List all wellness plans"""
    return render(request, 'library/plans.html')

@login_required
def plan_detail(request, slug):
    """Show detailed wellness plan"""
    return render(request, 'library/plan_detail.html')

@login_required
def user_progress(request):
    """Show user's progress across all resources and plans"""
    return render(request, 'library/progress.html')

@login_required
def user_bookmarks(request):
    """Show user's bookmarked resources"""
    return render(request, 'library/bookmarks.html')
