from django.urls import path
from . import views

app_name = 'professional'

urlpatterns = [
    # Dashboard
    path('', views.professional_dashboard, name='dashboard'),
    
    # Therapist search and booking
    path('therapists/', views.therapist_search, name='therapist-search'),
    path('therapists/<int:therapist_id>/', views.therapist_detail, name='therapist-detail'),
    path('therapists/<int:therapist_id>/book/', views.book_appointment, name='book-appointment'),
    
    # Appointments
    path('appointments/', views.appointment_list, name='appointment-list'),
    path('appointments/<uuid:appointment_id>/', views.appointment_detail, name='appointment-detail'),
    path('appointments/<uuid:appointment_id>/cancel/', views.cancel_appointment, name='cancel-appointment'),
    path('appointments/<uuid:appointment_id>/review/', views.leave_review, name='leave-review'),
    
    # Therapy goals
    path('goals/', views.therapy_goals, name='therapy-goals'),
    path('goals/<int:goal_id>/progress/', views.update_goal_progress, name='update-goal-progress'),
]
