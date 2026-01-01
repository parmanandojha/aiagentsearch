"""
Vercel serverless function entry point for Django
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_discovery.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
from django.conf import settings

# Initialize Django
application = get_wsgi_application()

def handler(request):
    """Vercel serverless function handler"""
    from django.core.handlers.wsgi import WSGIHandler
    from django.http import HttpResponse
    from django.urls import resolve
    from django.test import RequestFactory
    
    # Create a WSGI request from Vercel's request
    factory = RequestFactory()
    django_request = factory.request(
        REQUEST_METHOD=request.method,
        PATH_INFO=request.path,
        QUERY_STRING=request.query_string or '',
        **request.headers
    )
    
    # Process through Django
    handler = WSGIHandler()
    response = handler(django_request)
    
    return response

