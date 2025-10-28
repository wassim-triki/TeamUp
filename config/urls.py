"""
URL configuration for TeamUp project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public site / landing
    path('', include('apps.core.urls')),

    # Accounts and auth (users app) - Changed back to 'accounts/'
    path('accounts/', include('apps.users.urls')),

    # Sessions
    path('sessions/', include('apps.sessions.urls')),

    # API endpoints
    path('api/', include('apps.api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)