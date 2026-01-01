"""
Vercel serverless function for Django
WARNING: Vercel is NOT recommended for Django - use Railway or Render instead
"""
import os
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_discovery.settings')

# Initialize Django
import django
django.setup()

from django.core.wsgi import get_wsgi_application
from django.test import RequestFactory
from django.http import JsonResponse

# Get WSGI application
application = get_wsgi_application()
factory = RequestFactory()

def handler(request):
    """Vercel serverless function handler"""
    try:
        # Extract request details
        path = getattr(request, 'path', '/') or '/'
        method = getattr(request, 'method', 'GET') or 'GET'
        
        # Get query string
        query_string = ''
        if hasattr(request, 'query') and request.query:
            query_parts = []
            for key, value in request.query.items():
                if isinstance(value, list):
                    query_parts.extend([f"{key}={v}" for v in value])
                else:
                    query_parts.append(f"{key}={value}")
            query_string = '&'.join(query_parts)
        
        # Get headers
        headers = {}
        if hasattr(request, 'headers'):
            headers = dict(request.headers)
        
        # Create Django request
        django_request = factory.generic(
            method=method,
            path=path,
            data=getattr(request, 'body', b''),
            content_type=headers.get('Content-Type', 'text/plain'),
            **{f'HTTP_{k.upper().replace("-", "_")}': v for k, v in headers.items() if k != 'Content-Type'}
        )
        
        # Add query parameters
        if query_string:
            from urllib.parse import parse_qs
            django_request.GET = type(django_request.GET)()
            for key, values in parse_qs(query_string).items():
                for value in values:
                    django_request.GET.appendlist(key, value)
        
        # Process request through Django
        from django.core.handlers.base import BaseHandler
        handler = BaseHandler()
        handler.load_middleware()
        response = handler.get_response(django_request)
        
        # Convert Django response to Vercel format
        body = b''
        if hasattr(response, 'content'):
            body = response.content
        elif hasattr(response, 'getvalue'):
            body = response.getvalue()
        else:
            body = str(response).encode('utf-8')
        
        # Get response headers
        response_headers = {}
        for key, value in response.items():
            response_headers[key] = value
        
        return {
            'statusCode': response.status_code,
            'headers': response_headers,
            'body': body.decode('utf-8', errors='replace')
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"Serverless Function Error:\n{str(e)}\n\n{error_details}"
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': error_msg
        }
