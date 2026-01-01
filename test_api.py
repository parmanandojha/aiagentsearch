#!/usr/bin/env python3
"""
Test script to verify Google Maps Places API is enabled and working
"""
import googlemaps
import config
import sys

def test_api():
    """Test if Places API is enabled and working"""
    api_key = config.GOOGLE_MAPS_API_KEY
    
    if not api_key:
        print("❌ ERROR: No API key found in config.py")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    print("\n" + "="*60)
    print("Testing Google Maps Places API...")
    print("="*60 + "\n")
    
    try:
        # Initialize client
        gmaps = googlemaps.Client(key=api_key)
        print("✅ Google Maps client initialized")
        
        # Test Places API with a simple query
        print("\n🔍 Testing Places API with query: 'restaurants in New York'")
        places_result = gmaps.places(query='restaurants in New York')
        
        # Check status
        if 'status' in places_result:
            status = places_result['status']
            print(f"\n📊 API Status: {status}")
            
            if status == 'OK':
                print("✅ SUCCESS! Places API is enabled and working!")
                if 'results' in places_result:
                    count = len(places_result['results'])
                    print(f"✅ Found {count} results")
                    if count > 0:
                        first = places_result['results'][0]
                        print(f"\n📌 Example result:")
                        print(f"   Name: {first.get('name', 'N/A')}")
                        print(f"   Address: {first.get('formatted_address', 'N/A')}")
                return True
                
            elif status == 'REQUEST_DENIED':
                print("\n❌ ERROR: REQUEST_DENIED")
                print("\n⚠️  Places API is NOT enabled for this API key!")
                print("\n🔧 To fix this:")
                print("1. Go to: https://console.cloud.google.com/google/maps-apis")
                print("2. Select your project")
                print("3. Click 'Enable APIs and Services'")
                print("4. Search for 'Places API' and click ENABLE")
                print("5. Also enable 'Places API (New)' if available")
                print("6. Wait 2-5 minutes for activation")
                return False
                
            elif status == 'INVALID_REQUEST':
                print("❌ ERROR: INVALID_REQUEST - Check your query format")
                return False
                
            elif status == 'OVER_QUERY_LIMIT':
                print("❌ ERROR: OVER_QUERY_LIMIT - API quota exceeded")
                print("   Check your billing/quota in Google Cloud Console")
                return False
                
            elif status == 'ZERO_RESULTS':
                print("⚠️  ZERO_RESULTS - API is working but no results found")
                print("   This is OK - the API is enabled and responding")
                return True
                
            else:
                print(f"❌ ERROR: Unexpected status '{status}'")
                if 'error_message' in places_result:
                    print(f"   Message: {places_result['error_message']}")
                return False
        else:
            print("⚠️  No status field in response")
            print(f"Response keys: {list(places_result.keys())}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {type(e).__name__}")
        print(f"   Error: {str(e)}")
        
        error_str = str(e).lower()
        if 'api key' in error_str or 'invalid' in error_str:
            print("\n⚠️  Possible issues:")
            print("- API key is invalid")
            print("- Places API is not enabled")
            print("- Billing is not enabled")
        
        return False

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Google Maps Places API Test")
    print("="*60 + "\n")
    
    success = test_api()
    
    print("\n" + "="*60)
    if success:
        print("✅ API TEST PASSED - You can run the agent now!")
    else:
        print("❌ API TEST FAILED - Please fix the issues above")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)


