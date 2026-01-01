# Django Setup - Quick Start Guide

## ✅ What's Been Created

Your application has been fully converted to Django with:

- **Backend**: Django views and API endpoints
- **Frontend**: Django templates with separated CSS/JS
- **API**: `/api/search` endpoint for business discovery
- **Static Files**: Organized CSS and JavaScript files

## 🚀 Quick Start

### 1. Install Django and Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations (Optional - for database features)

```bash
python manage.py migrate
```

### 3. Start the Django Server

```bash
python manage.py runserver
```

Or use the convenience script:
```bash
./run_django.sh
```

### 4. Access the Application

Open your browser and go to:
**http://localhost:8000**

## 📁 Project Structure

```
business_discovery/          # Django project settings
├── settings.py             # Main settings (API key configured)
├── urls.py                 # URL routing
└── wsgi.py                 # WSGI config

discovery_app/              # Main Django app
├── views.py                # API and page views
├── urls.py                 # App URLs
└── apps.py                 # App config

templates/
└── discovery_app/
    └── index.html         # Main page template

static/                     # Static files
├── css/
│   └── main.css          # Styles
└── js/
    └── main.js           # JavaScript

manage.py                   # Django management script
```

## 🔧 Configuration

**Configure your Google Maps API key:**
- Create a `.env` file in the project root
- Add: `GOOGLE_MAPS_API_KEY=your-api-key-here`
- Get your API key from: https://console.cloud.google.com/google/maps-apis
- **Never commit your API key to version control!**

## 🌐 API Endpoint

**POST** `/api/search`

Request body:
```json
{
    "industry": "restaurants",
    "location": "New York, NY",
    "max_results": 20
}
```

Response:
```json
{
    "summary": {...},
    "businesses": [...]
}
```

## ✨ Features

- ✅ Clean Django architecture
- ✅ RESTful API endpoint
- ✅ Modern, responsive UI
- ✅ Error handling
- ✅ Results saved to `results.json`
- ✅ Static file organization
- ✅ CSRF protection (disabled for API with @csrf_exempt)

## 📝 Notes

- The old `server.py` and `view_results.html` files are still present but not used by Django
- Results are saved to both `results.json` (project root) and `static/results.json`
- No database required - can be added later for search history

## 🐛 Troubleshooting

**ImportError: No module named 'django'**
- Run: `pip install -r requirements.txt`

**Template not found**
- Make sure `templates/discovery_app/index.html` exists
- Check `settings.py` has `'discovery_app'` in `INSTALLED_APPS`

**Static files not loading**
- Run: `python manage.py collectstatic` (optional for development)
- In development, Django serves static files automatically

**Port already in use**
- Kill the old server: `lsof -ti:8000 | xargs kill -9`
- Or use a different port: `python manage.py runserver 8001`


