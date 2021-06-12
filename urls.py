from django.contrib import admin
from django.urls import path, include
from .views import Page, DoctorRegister, UserEdit, PasswordChange
from django.contrib.auth import views as auth_views

app_name = 'users'
urlpatterns = [
        path('dregister/', DoctorRegister.as_view(), name='DRegister'),
        path('edit_profile/', UserEdit.as_view(), name='Edit'),
        path('password/', PasswordChange.as_view(template_name='registration/changep.html')),
        path('dpage/', Page.as_view(), name='Doctor'),
    ]
