"""
URL configuration for business_discovery project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('discovery_app.urls')),
]

# Serve static files during development
if settings.DEBUG:
    # Serve static files from STATICFILES_DIRS (the static/ directory)
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()

