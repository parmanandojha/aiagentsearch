# Check API Status

## Quick Test Command

Run this in your terminal to test if Places API is enabled:

```bash
python3 quick_test.py
```

## Expected Results

### ✅ If API is enabled:
```
Status: OK
✅ SUCCESS! Places API is enabled!
Found X results
```

### ❌ If API is NOT enabled:
```
Status: REQUEST_DENIED
❌ Places API NOT enabled. Enable it at:
https://console.cloud.google.com/google/maps-apis
```

## How to Enable Places API

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/google/maps-apis
   - Or: https://console.cloud.google.com/apis/library

2. **Enable Places API:**
   - Click "Enable APIs and Services" (or "APIs & Services" > "Library")
   - Search for **"Places API"**
   - Click on **"Places API"**
   - Click **"ENABLE"** button

3. **Enable Places API (New):**
   - Also search for **"Places API (New)"**
   - Enable it as well (this is the newer version)

4. **Wait 2-5 minutes** for activation

5. **Check Billing:**
   - Go to: https://console.cloud.google.com/billing
   - Make sure billing account is linked to your project
   - Free tier: $200/month credit (usually enough for testing)

## Test Again

After enabling, run the test again:
```bash
python3 quick_test.py
```

Or run the full agent:
```bash
python3 run_with_key.py "restaurants" "New York, NY" 5
```


