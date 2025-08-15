from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def community_home(request):
    return render(request, 'community/home.html')

@login_required
def support_groups(request):
    return render(request, 'community/groups.html')

@login_required
def group_detail(request, group_id):
    return render(request, 'community/group_detail.html', {'group_id': group_id})
