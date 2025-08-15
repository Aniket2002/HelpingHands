from django.contrib import admin
from .models import CustomUser, UserProfile, TherapistCredentials

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'user_type', 'is_verified', 'last_activity')
    list_filter = ('user_type', 'is_verified', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_activity', 'created_at', 'updated_at')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'experience_years', 'is_accepting_clients')
    list_filter = ('is_accepting_clients', 'user__user_type')
    search_fields = ('user__email', 'user__first_name', 'specialization')

@admin.register(TherapistCredentials)
class TherapistCredentialsAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_status', 'verified_at')
    list_filter = ('verification_status',)
    search_fields = ('user__email', 'user__first_name')
