"""
Configuration file for the Business Discovery Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys (MUST be set in .env file - no default for security)
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
if not GOOGLE_MAPS_API_KEY:
    raise ValueError(
        "GOOGLE_MAPS_API_KEY environment variable is required! "
        "Set it in a .env file or as an environment variable. "
        "Never hardcode API keys in source code."
    )

# Default settings
DEFAULT_MAX_RESULTS = 50
DEFAULT_WEBSITE_REQUIRED = False
DEFAULT_TIMEOUT = 10

# User agent for web scraping
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Scoring thresholds
SCORE_THRESHOLDS = {
    'high_potential': 7.0,  # Above this is "High Potential"
    'needs_redesign': 4.0,  # Below this is "Needs Redesign"
    # Between 4.0 and 7.0 is "Digitally Mature"
}

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 1

