from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('wellness/', include('apps.wellness.urls')),
    path('chat/', include('apps.chat.urls')),
    path('appointments/', include('apps.appointments.urls')),
    path('community/', include('apps.community.urls')),
    path('professional/', include('apps.professional.urls')),
    path('library/', include('apps.library.urls')),
    path('privacy/', include('apps.privacy.urls')),
    path('', include('apps.authentication.urls')),  # Frontend routes
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
