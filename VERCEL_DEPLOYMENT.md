# Vercel Deployment Guide for Django

## ⚠️ Important Note

**Vercel is NOT recommended for Django applications.** Vercel is optimized for serverless functions and static sites, not long-running WSGI applications like Django.

**Recommended platforms for Django:**
- **Railway** (easiest) - https://railway.app
- **Render** (free tier) - https://render.com
- **PythonAnywhere** (free tier) - https://www.pythonanywhere.com

## If You Must Use Vercel

Vercel requires special configuration. Follow these steps:

### 1. Environment Variables in Vercel Dashboard

Go to your Vercel project settings and add these environment variables:

```
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=aiagentsearch.vercel.app,*.vercel.app
```

### 2. Update ALLOWED_HOSTS

Make sure `ALLOWED_HOSTS` in `business_discovery/settings.py` includes your Vercel domain:

```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

In Vercel dashboard, set:
```
ALLOWED_HOSTS=aiagentsearch.vercel.app,*.vercel.app
```

### 3. Static Files

Vercel may have issues with Django static files. You may need to:
- Run `python manage.py collectstatic` before deployment
- Or configure static file serving differently

### 4. Limitations

- **No WebSockets**: Vercel serverless functions don't support WebSockets
- **Cold Starts**: First request may be slow
- **Timeouts**: Long-running requests may timeout
- **Database**: SQLite won't work on Vercel (use external database)

### 5. Better Alternative: Railway

1. Go to https://railway.app
2. Sign up and create new project
3. Connect your GitHub repository
4. Railway auto-detects Django
5. Add environment variables
6. Deploy!

Railway is much better suited for Django applications.

