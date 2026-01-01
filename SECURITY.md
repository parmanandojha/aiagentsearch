# Security Configuration

## SECRET_KEY Security

The SECRET_KEY is now securely managed:

1. **Development**: Automatically generates a new random key if not set
2. **Production**: REQUIRES `SECRET_KEY` environment variable to be set
3. **Generation**: Use this command to generate a secure key:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

### Setting SECRET_KEY

**For Local Development:**
- Optional: Create a `.env` file with `SECRET_KEY=your-generated-key`
- Or let Django auto-generate one (not recommended for production)

**For Production:**
- MUST set `SECRET_KEY` environment variable
- Application will fail to start if not set in production mode

## Rate Limiting

Rate limiting is configured to prevent abuse:

- **Limit**: 10 requests per hour per IP address
- **Applies to**: `/api/search/stream` endpoint
- **Response**: HTTP 429 (Too Many Requests) when limit exceeded

### Adjusting Rate Limits

Edit the decorator in `discovery_app/views.py`:
```python
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
```

Common rate formats:
- `'10/h'` - 10 per hour
- `'10/m'` - 10 per minute
- `'100/d'` - 100 per day

## Environment Variables

Required for production:
```bash
SECRET_KEY=your-secret-key-here
GOOGLE_MAPS_API_KEY=your-api-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

## Installation

After pulling the latest code, install the rate limiting package:
```bash
pip install django-ratelimit==4.1.0
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

