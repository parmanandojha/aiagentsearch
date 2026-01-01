# Deployment Guide

This Django application can be deployed to various platforms. **Vercel is NOT recommended** as it doesn't natively support Django applications.

## 🚀 Recommended Platforms

### Option 1: Railway (Easiest - Recommended)

Railway makes Django deployment very simple:

1. **Sign up at Railway**: https://railway.app
2. **Install Railway CLI** (optional):
   ```bash
   npm install -g @railway/cli
   ```
3. **Deploy**:
   - Go to Railway dashboard
   - Click "New Project"
   - Connect your GitHub repository (or upload files)
   - Railway will auto-detect Django
   - Add environment variable: `GOOGLE_MAPS_API_KEY=your_key_here`
   - Deploy!

**Pricing**: Free tier with $5 credit/month

---

### Option 2: Render (Free Tier Available)

1. **Sign up at Render**: https://render.com
2. **Create New Web Service**:
   - Connect your GitHub repository
   - Select "Web Service"
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start Command: `gunicorn business_discovery.wsgi:application`
   - Add environment variables:
     - `GOOGLE_MAPS_API_KEY=your_key_here`
     - `SECRET_KEY=your-secret-key-here` (generate one)
     - `DEBUG=False`
     - `ALLOWED_HOSTS=your-app.onrender.com`

**Pricing**: Free tier available (spins down after inactivity)

---

### Option 3: PythonAnywhere

1. **Sign up**: https://www.pythonanywhere.com
2. **Upload your code** via git or files
3. **Set up virtual environment**
4. **Configure WSGI file**
5. **Set environment variables**

**Pricing**: Free tier available

---

## 📋 Pre-Deployment Checklist

Before deploying, update these settings in `business_discovery/settings.py`:

```python
# Set DEBUG to False
DEBUG = False

# Set ALLOWED_HOSTS to your domain
ALLOWED_HOSTS = ['your-domain.com', 'your-app.railway.app']

# Use environment variable for SECRET_KEY
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
```

## 🔐 Environment Variables to Set

- `GOOGLE_MAPS_API_KEY` - Your Google Maps API key (required)
- `SECRET_KEY` - Django secret key (generate a new one for production)
- `DEBUG` - Set to `False` for production
- `ALLOWED_HOSTS` - Your domain(s)

## 📝 Generate Secret Key

Run this to generate a secure secret key:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## 🚫 Why Not Vercel?

Vercel is optimized for:
- Serverless functions (Node.js, Python functions)
- Static sites
- Next.js, React, Vue apps

Vercel does NOT support:
- Long-running Django processes
- WebSocket connections (needed for some Django features)
- Traditional WSGI applications

While you *could* use Vercel's serverless functions, it would require a complete rewrite of your Django app, which is not practical.

## ✅ Quick Deploy to Railway

1. Push your code to GitHub
2. Go to https://railway.app
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Django
6. Add environment variable: `GOOGLE_MAPS_API_KEY`
7. Click "Deploy"
8. Done! 🎉

Your app will be live at: `https://your-app.up.railway.app`

