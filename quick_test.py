#!/usr/bin/env python3
"""Quick API test - run this in your terminal"""
import googlemaps
import config

api_key = config.GOOGLE_MAPS_API_KEY
print(f"API Key: {api_key[:20]}...")

try:
    gmaps = googlemaps.Client(key=api_key)
    print("Testing Places API...")
    
    result = gmaps.places(query='coffee shops in San Francisco')
    status = result.get('status', 'UNKNOWN')
    
    print(f"\nStatus: {status}")
    
    if status == 'OK':
        print("✅ SUCCESS! Places API is enabled!")
        print(f"Found {len(result.get('results', []))} results")
    elif status == 'REQUEST_DENIED':
        print("❌ Places API NOT enabled. Enable it at:")
        print("https://console.cloud.google.com/google/maps-apis")
    else:
        print(f"Response: {status}")
        
except Exception as e:
    print(f"Error: {e}")


