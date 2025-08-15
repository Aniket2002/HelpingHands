from django.urls import path
from . import views

app_name = 'privacy'

urlpatterns = [
    path('', views.privacy_dashboard, name='dashboard'),
    path('settings/', views.privacy_settings, name='settings'),
    path('data-export/', views.request_data_export, name='data-export'),
    path('data-deletion/', views.request_data_deletion, name='data-deletion'),
    path('access-log/', views.access_log, name='access-log'),
    path('security-incidents/', views.security_incidents, name='security-incidents'),
]
