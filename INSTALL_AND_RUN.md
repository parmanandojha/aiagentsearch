# Quick Install and Run Guide

## Step 1: Install Dependencies

```bash
pip3 install -r requirements.txt
```

Or use a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Run the Agent

Your API key is already configured in `run_with_key.py`. Run it with:

```bash
python3 run_with_key.py
```

Or customize the search:
```bash
python3 run_with_key.py "restaurants" "New York, NY" 10
```

## Configure API Key

**You must set your Google Maps API key before running the application:**

1. Create a `.env` file in the project root directory
2. Add your API key:
   ```
   GOOGLE_MAPS_API_KEY=your-api-key-here
   ```
3. Get your API key from: https://console.cloud.google.com/google/maps-apis
4. **Never commit your API key to version control!**

## Alternative: Use Command Line (if dependencies installed)

```bash
python3 agent.py \
  --industry "coffee shops" \
  --location "San Francisco, CA" \
  --max-results 5 \
  --api-key your-api-key-here
```

Or set it in `.env` and use without --api-key flag.


