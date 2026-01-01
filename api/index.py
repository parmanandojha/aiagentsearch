"""
Vercel serverless function entry point for Django
This is a workaround - Vercel is NOT ideal for Django applications.
For better results, use Railway or Render instead.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_discovery.settings')

# Import Django
import django
django.setup()

from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from django.urls import resolve
from django.test import RequestFactory

# Get WSGI application
application = get_wsgi_application()

# Create request factory
factory = RequestFactory()

def handler(request):
    """
    Vercel serverless function handler
    Converts Vercel request to Django request and returns Django response
    """
    try:
        # Build Django request from Vercel request
        path = request.path or '/'
        method = request.method or 'GET'
        
        # Get query string
        query_string = ''
        if hasattr(request, 'query') and request.query:
            query_string = '&'.join([f"{k}={v}" for k, v in request.query.items()])
        
        # Create Django request
        django_request = factory.request(
            REQUEST_METHOD=method,
            PATH_INFO=path,
            QUERY_STRING=query_string,
            **getattr(request, 'headers', {})
        )
        
        # Process through Django
        from django.core.handlers.base import BaseHandler
        handler = BaseHandler()
        handler.load_middleware()
        response = handler.get_response(django_request)
        
        # Convert Django response to Vercel format
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.content.decode('utf-8') if hasattr(response, 'content') else str(response)
        }
        
    except Exception as e:
        import traceback
        error_msg = f"Error in Django handler: {str(e)}\n{traceback.format_exc()}"
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': error_msg
        }
