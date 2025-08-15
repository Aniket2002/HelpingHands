from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.wellness_library, name='home'),
    path('categories/', views.category_list, name='categories'),
    path('categories/<slug:category_slug>/', views.category_detail, name='category-detail'),
    path('resources/<slug:slug>/', views.resource_detail, name='resource-detail'),
    path('plans/', views.plan_list, name='plans'),
    path('plans/<slug:slug>/', views.plan_detail, name='plan-detail'),
    path('my-progress/', views.user_progress, name='user-progress'),
    path('bookmarks/', views.user_bookmarks, name='bookmarks'),
]
