from django.urls import path
from . import views

urlpatterns = [
    path('', views.wellness_dashboard, name='wellness-dashboard'),
    path('mood/', views.mood_entries, name='mood-entries'),
    path('goals/', views.wellness_goals, name='wellness-goals'),
    path('resources/', views.wellness_resources, name='wellness-resources'),
]
