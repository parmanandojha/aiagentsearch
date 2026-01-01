# Django Business Discovery Agent

Complete Django implementation of the Business Discovery Agent with frontend and backend.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations (Optional - using SQLite)

```bash
python manage.py migrate
```

### 3. Run Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://localhost:8000**

## Project Structure

```
business_discovery/
├── business_discovery/     # Django project settings
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── discovery_app/          # Main Django app
│   ├── views.py           # Views (API endpoints)
│   ├── urls.py            # App URLs
│   └── apps.py            # App configuration
├── templates/              # HTML templates
│   └── discovery_app/
│       └── index.html     # Main template
├── static/                 # Static files (CSS, JS)
│   ├── css/
│   │   └── main.css       # Styles
│   └── js/
│       └── main.js        # JavaScript
├── agent.py               # Business discovery agent
├── discovery.py           # Business discovery module
├── contact_extractor.py   # Contact extraction
├── social_discovery.py    # Social media discovery
├── auditor.py             # Website audit
├── scoring.py             # Scoring module
├── formatter.py           # Output formatting
├── config.py              # Configuration
└── manage.py              # Django management script
```

## Features

- **Django Backend**: Clean, maintainable Django views
- **RESTful API**: `/api/search` endpoint for search requests
- **Modern Frontend**: Beautiful, responsive UI
- **Static Files**: Separated CSS and JavaScript
- **CSRF Protection**: Django's built-in CSRF protection
- **Error Handling**: Comprehensive error handling

## Usage

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```

2. **Access the application:**
   - Open: http://localhost:8000
   - Use the search form to find businesses

3. **API Endpoint:**
   - POST `/api/search`
   - Body: `{"industry": "restaurants", "location": "New York, NY", "max_results": 20}`

## Configuration

Set your Google Maps API key in `.env` file:
```
GOOGLE_MAPS_API_KEY=your_api_key_here
```

Or in `business_discovery/settings.py` (already configured with default key).

## Production Deployment

For production:
1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Use a proper database (PostgreSQL recommended)
4. Set up static file serving (collectstatic)
5. Use a production WSGI server (Gunicorn + Nginx)

## Notes

- Results are saved to `results.json` in the project root
- Static files are served from the `static/` directory
- The app doesn't require a database (can be added if needed for storing search history)


