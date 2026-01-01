"""
ASGI config for business_discovery project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'business_discovery.settings')

application = get_asgi_application()


