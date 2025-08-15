from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('register/client/', views.client_register_view, name='client_register'),
    path('register/therapist/', views.therapist_register_view, name='therapist_register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    
    # Settings sub-pages
    path('settings/password/', views.change_password_view, name='change_password'),
    path('settings/email/', views.email_preferences_view, name='email_preferences'),
    path('settings/privacy/', views.privacy_settings_view, name='privacy_settings'),
    path('settings/notifications/', views.notification_settings_view, name='notification_settings'),
    path('settings/download/', views.download_data_view, name='download_data'),
    path('settings/availability/', views.availability_settings_view, name='availability_settings'),
    path('settings/theme/', views.theme_preferences_view, name='theme_preferences'),
    path('settings/language/', views.language_settings_view, name='language_settings'),
]
