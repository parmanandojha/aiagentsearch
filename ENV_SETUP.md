# Environment Setup Guide

This guide explains how to set up and use environment variables for development and production modes.

## 📁 Environment Files

The project includes the following environment files:

- **`.env.example`** - Template file (safe to commit to git)
- **`.env.development`** - Example for development/debug mode
- **`.env.production`** - Example for production mode
- **`.env`** - Your actual environment file (DO NOT commit to git)

## 🛠️ Setup Instructions

### Step 1: Generate a SECRET_KEY

Generate a secure SECRET_KEY using Django's utility:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output - you'll need it for your .env file.

### Step 2: Create Your .env File

**For Development/Debug Mode:**
```bash
cp .env.development .env
```

Then edit `.env` and replace:
- `SECRET_KEY` with your generated key
- `GOOGLE_MAPS_API_KEY` with your actual API key

**For Production:**
```bash
cp .env.production .env
```

Then edit `.env` and replace:
- `SECRET_KEY` with a strong production key
- `GOOGLE_MAPS_API_KEY` with your production API key
- `ALLOWED_HOSTS` with your actual domain(s)
- Ensure `DEBUG=False`

## 🚀 Running the Server

### Development/Debug Mode

**Option 1: Using .env file (Recommended)**
```bash
# Make sure .env has DEBUG=True
cp .env.development .env
# Edit .env and add your SECRET_KEY and GOOGLE_MAPS_API_KEY
python3 manage.py runserver 0.0.0.0:8000
```

**Option 2: Using environment variable**
```bash
DEBUG=True python3 manage.py runserver 0.0.0.0:8000
```

**Option 3: Export environment variable**
```bash
export DEBUG=True
python3 manage.py runserver 0.0.0.0:8000
```

### Production Mode

**Option 1: Using .env file**
```bash
# Make sure .env has DEBUG=False
cp .env.production .env
# Edit .env with production values
python3 manage.py runserver 0.0.0.0:8000
```

**Option 2: Using environment variable**
```bash
DEBUG=False python3 manage.py runserver 0.0.0.0:8000
```

**Option 3: Using Gunicorn (Recommended for production)**
```bash
# Set environment variables
export DEBUG=False
export SECRET_KEY=your-production-secret-key
export GOOGLE_MAPS_API_KEY=your-production-api-key
export ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Run with Gunicorn
gunicorn business_discovery.wsgi:application --bind 0.0.0.0:8000
```

## 📋 Environment Variables Reference

| Variable | Development | Production | Required |
|----------|------------|------------|----------|
| `SECRET_KEY` | Any (auto-generated if not set) | Strong unique key | ✅ Yes |
| `GOOGLE_MAPS_API_KEY` | Your API key | Production API key | ✅ Yes |
| `DEBUG` | `True` | `False` | ⚠️ Recommended |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Your domain(s) | ⚠️ Recommended |

## 🔍 Quick Check

To verify your environment is set up correctly:

```bash
# Check if .env file exists
ls -la .env

# View environment variables (without exposing secrets)
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('DEBUG:', os.getenv('DEBUG')); print('ALLOWED_HOSTS:', os.getenv('ALLOWED_HOSTS'))"
```

## ⚠️ Security Notes

1. **Never commit `.env` files to git** - They're already in `.gitignore`
2. **Use different SECRET_KEY for production** - Generate a new one
3. **Never set DEBUG=True in production** - Security risk!
4. **Set ALLOWED_HOSTS in production** - Prevent Host header attacks
5. **Keep API keys secure** - Don't share or expose them

## 🌐 Deployment Platforms

### Railway / Render / Heroku

Set environment variables in your platform's dashboard:
- Go to your project settings
- Add environment variables:
  - `SECRET_KEY`
  - `GOOGLE_MAPS_API_KEY`
  - `DEBUG=False`
  - `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`

The platform will automatically use these variables - no `.env` file needed!

## 🔄 Switching Between Modes

**Switch to Debug Mode:**
```bash
cp .env.development .env
# Edit .env if needed
python3 manage.py runserver
```

**Switch to Production Mode:**
```bash
cp .env.production .env
# Edit .env with production values
python3 manage.py runserver
```

Or use environment variables directly without copying files:
```bash
DEBUG=True python3 manage.py runserver    # Debug mode
DEBUG=False python3 manage.py runserver   # Production mode
```

