from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_home, name='community-home'),
    path('groups/', views.support_groups, name='support-groups'),
    path('groups/<int:group_id>/', views.group_detail, name='group-detail'),
]
