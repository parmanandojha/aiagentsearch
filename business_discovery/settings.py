"""
Django settings for business_discovery project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
# Default to False for security - set DEBUG=True in .env for development
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# SECURITY WARNING: keep the secret key used in production secret!
# Use environment variable SECRET_KEY, or generate a new one for development
SECRET_KEY = os.getenv('SECRET_KEY', None)
if not SECRET_KEY:
    if DEBUG:
        # Generate a new secret key for development only (not secure for production!)
        from django.core.management.utils import get_random_secret_key
        SECRET_KEY = get_random_secret_key()
        print("⚠️  WARNING: SECRET_KEY auto-generated for development. Set SECRET_KEY in .env for production!")
    else:
        # Production mode requires explicit SECRET_KEY
        raise ValueError(
            "SECRET_KEY environment variable must be set in production! "
            "Generate one with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
        )

# Security: ALLOWED_HOSTS should be set via environment variable in production
# For development, allow localhost (covers localhost:8000, localhost:8080, etc.)
# Note: ALLOWED_HOSTS only needs the hostname, not protocol (http/https) or port
# For production, set specific domains.
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'discovery_app',
    'django_ratelimit',  # Rate limiting for API endpoints
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Note: django-ratelimit uses decorators (@ratelimit), not middleware
]

ROOT_URLCONF = 'business_discovery.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'business_discovery.wsgi.application'

# Database (optional - not using for now)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache Configuration (Required for django-ratelimit)
# django-ratelimit requires a cache backend that supports atomic increment
# Options: Redis (recommended), Memcached, or use dummy cache for development

# Try to use Redis if available, otherwise fall back to dummy cache for development
try:
    import django_redis
    import redis
    # Redis is available - use it
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
            'TIMEOUT': 3600,  # 1 hour (matches rate limit of 10/hour)
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
    print("✅ Using Redis cache backend for rate limiting")
except ImportError:
    # Redis not available - use dummy cache for development
    # Note: Rate limiting will not work properly with dummy cache
    # Install Redis for proper rate limiting: pip install django-redis redis
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    print("⚠️  WARNING: Using DummyCache - rate limiting will not work properly!")
    print("⚠️  Install Redis for proper rate limiting:")
    print("⚠️    1. Install Redis: brew install redis (macOS) or apt-get install redis-server (Linux)")
    print("⚠️    2. Start Redis: brew services start redis (macOS) or systemctl start redis (Linux)")
    print("⚠️    3. Install Python packages: pip install django-redis redis")

# Password validation (not using authentication, but required)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Static files finders (for development)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security Settings
# =================

# Security Headers
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # Redirect HTTP to HTTPS in production
    SESSION_COOKIE_SECURE = True  # Only send session cookies over HTTPS
    CSRF_COOKIE_SECURE = True  # Only send CSRF cookies over HTTPS
    SECURE_BROWSER_XSS_FILTER = True  # Enable browser's XSS filter
    SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
    X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking (already set by middleware, but explicit here)
    SECURE_HSTS_SECONDS = 31536000  # 1 year - Force HTTPS for 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # Development settings
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    X_FRAME_OPTIONS = 'SAMEORIGIN'  # Allow in same origin for development

# Session Security
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookies
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF Settings
CSRF_COOKIE_HTTPONLY = False  # Must be False for AJAX requests to work
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False

# Content Security Policy (CSP) - Basic implementation
# For more complex sites, use django-csp middleware
if not DEBUG:
    # In production, you may want to add CSP headers via middleware
    # This is a basic implementation - consider django-csp for more control
    pass

# Google Maps API Key (MUST be set via environment variable - never hardcode!)
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
if not GOOGLE_MAPS_API_KEY:
    raise ValueError(
        "GOOGLE_MAPS_API_KEY environment variable is required! "
        "Set it in a .env file or as an environment variable. "
        "Never hardcode API keys in source code."
    )

