# Redis Setup for Rate Limiting

## Problem

django-ratelimit requires a cache backend that supports **atomic increment operations**. The following backends do NOT work:
- ❌ LocMemCache (not shared)
- ❌ FileBasedCache (no atomic increment)
- ❌ DatabaseCache (no atomic increment)

## Solution: Install Redis

Redis is the recommended cache backend for django-ratelimit.

### Step 1: Install Redis

**On macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
```

**On Windows:**
Download from: https://redis.io/download
Or use WSL (Windows Subsystem for Linux)

### Step 2: Install Python Redis Packages

```bash
pip install django-redis redis
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 3: Verify Redis is Running

```bash
redis-cli ping
```

Should return: `PONG`

### Step 4: Restart Django Server

```bash
python3 manage.py runserver 0.0.0.0:8000
```

## Current Configuration

The settings.py file is already configured to:
1. Try to use Redis if available
2. Fall back to DummyCache if Redis is not installed (rate limiting won't work)

## Verify It's Working

After installing Redis and restarting the server, you should see:
- ✅ No cache backend errors
- ✅ Rate limiting working properly (1 request per 2 hours)

## Alternative: Use Memcached

If you prefer Memcached:

1. Install Memcached:
   ```bash
   # macOS
   brew install memcached
   brew services start memcached
   
   # Linux
   sudo apt-get install memcached
   sudo systemctl start memcached
   ```

2. Install Python client:
   ```bash
   pip install python-memcached
   ```

3. Update settings.py:
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
           'LOCATION': '127.0.0.1:11211',
       }
   }
   ```

## Development Workaround

If you can't install Redis right now, the current configuration uses DummyCache which:
- ✅ Allows the server to start
- ❌ Rate limiting won't work properly
- ⚠️ You should install Redis for proper functionality

