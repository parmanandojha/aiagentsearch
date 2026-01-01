# 🔧 Google Maps API Setup Guide

## The Problem

You're seeing zero results because the **Places API is not enabled** for your API key.

## Solution: Enable Places API

### Step 1: Go to Google Cloud Console
Visit: https://console.cloud.google.com/google/maps-apis

### Step 2: Select Your Project
- If you don't have a project, create one
- Make sure you're using the project that contains your API key

### Step 3: Enable Places API
1. Click **"Enable APIs and Services"** (or "APIs & Services" > "Library")
2. Search for **"Places API"**
3. Click on **"Places API"**
4. Click **"ENABLE"** button
5. **Also enable "Places API (New)"** if you see it (this is the newer version)

### Step 4: Wait for Activation
- Wait 2-5 minutes for the API to activate
- You may need to refresh your browser

### Step 5: Verify API Key Restrictions (Optional but Recommended)
1. Go to **"APIs & Services" > "Credentials"**
2. Click on your API key
3. Under **"API restrictions"**:
   - Select **"Restrict key"**
   - Choose: **"Places API"** and **"Places API (New)"**
   - This limits what your key can access (security best practice)

### Step 6: Check Billing (If Needed)
- Google Maps APIs require billing to be enabled
- Free tier: $200 credit per month (usually enough for testing)
- Set up billing at: https://console.cloud.google.com/billing

## Verify It's Working

After enabling the API, run the agent again:

```bash
python3 run_with_key.py "restaurants" "New York, NY" 5
```

You should now see businesses being discovered!

## Required APIs

Make sure these are enabled:
- ✅ **Places API** (required for business search)
- ✅ **Places API (New)** (recommended, newer version)

## Common Error Messages

- `REQUEST_DENIED` → API not enabled or API key invalid
- `OVER_QUERY_LIMIT` → Too many requests, check billing/quota
- `ZERO_RESULTS` → No businesses found (this is normal, try different location)

## Need Help?

- Google Maps API Docs: https://developers.google.com/maps/documentation/places/web-service
- API Status: Check https://status.cloud.google.com/ if APIs seem down
