from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointments_list, name='appointments-list'),
    path('book/', views.book_appointment, name='book-appointment'),
    path('find-matches/', views.find_matches, name='find-matches'),
    path('preferences/', views.setup_preferences, name='setup-preferences'),
    path('therapist/<int:therapist_id>/', views.therapist_detail, name='therapist-detail'),
    path('<int:appointment_id>/', views.appointment_detail, name='appointment-detail'),
]
