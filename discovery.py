"""
Business Discovery Module
Searches for businesses by industry and location using Google Maps API
"""
import googlemaps
from typing import List, Dict, Optional
import config
import logging
import requests
import validators
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessDiscovery:
    """Discover businesses using Google Maps Places API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the discovery client
        
        Args:
            api_key: Google Maps API key. If None, uses config value
        """
        api_key = api_key or config.GOOGLE_MAPS_API_KEY
        if not api_key:
            logger.warning("No Google Maps API key provided. Discovery will use fallback methods.")
            self.gmaps = None
        else:
            try:
                self.gmaps = googlemaps.Client(key=api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps client: {e}")
                self.gmaps = None
    
    def search_businesses(
        self, 
        industry: str, 
        location: str, 
        max_results: int = config.DEFAULT_MAX_RESULTS,
        website_required: bool = config.DEFAULT_WEBSITE_REQUIRED,
        existing_place_ids: set = None,
        existing_business_keys: set = None
    ) -> List[Dict]:
        """
        Search for businesses by industry and location
        
        Args:
            industry: Business industry/type (e.g., "restaurants", "dentists")
            location: Geographic location (e.g., "New York, NY", "London, UK")
            max_results: Maximum number of results to return
            website_required: Only return businesses with websites
            
        Returns:
            List of business dictionaries with name, website, location
        """
        # Format query - ensure location has proper format
        if ',' not in location:
            # If location doesn't have a comma, it might need country/region
            # Try adding common suffixes
            query = f"{industry} in {location}"
        else:
            query = f"{industry} in {location}"
        businesses = []
        
        # Initialize sets if not provided
        if existing_place_ids is None:
            existing_place_ids = set()
        if existing_business_keys is None:
            existing_business_keys = set()
        
        try:
            if self.gmaps:
                businesses = self._search_google_maps(
                    query, max_results, website_required, 
                    existing_place_ids, existing_business_keys
                )
            else:
                businesses = self._search_fallback(
                    query, max_results, website_required,
                    existing_place_ids, existing_business_keys
                )
        except Exception as e:
            logger.error(f"Error during business discovery: {e}")
            businesses = self._search_fallback(
                query, max_results, website_required,
                existing_place_ids, existing_business_keys
            )
        
        return businesses[:max_results]
    
    def _search_google_maps(
        self, 
        query: str, 
        max_results: int, 
        website_required: bool,
        existing_place_ids: set = None,
        existing_business_keys: set = None
    ) -> List[Dict]:
        """Search using Google Maps Places API with pagination support"""
        businesses = []
        
        try:
            # Use Places API text search
            places_result = self.gmaps.places(query=query)
            
            # Check for API errors
            if 'status' in places_result:
                status = places_result['status']
                if status != 'OK' and status != 'ZERO_RESULTS':
                    error_msg = f"Google Maps API Error: {status}"
                    if status == 'REQUEST_DENIED':
                        error_msg += "\n\n⚠️  Places API is not enabled for your API key!"
                        error_msg += "\nPlease enable it in Google Cloud Console:"
                        error_msg += "\n1. Go to https://console.cloud.google.com/google/maps-apis"
                        error_msg += "\n2. Select your project"
                        error_msg += "\n3. Enable 'Places API' (or 'Places API (New)')"
                        error_msg += "\n4. Wait a few minutes for activation"
                    logger.error(error_msg)
                    return businesses
            
            # Process results with pagination
            next_page_token = None
            page_count = 0
            # Increase max_pages to account for duplicates - fetch more pages if needed
            # Each page has up to 20 results, so we need at least max_results/20 pages
            # Add extra buffer (50% more) to account for duplicates from history
            max_pages = int((max_results / 20) * 1.5) + 3  # More pages to account for duplicates
            
            # Track seen place_ids to avoid duplicates (within current search)
            seen_place_ids = set()
            seen_business_keys = set()  # Track name+location combinations for businesses without place_id
            
            # Initialize existing sets if not provided
            if existing_place_ids is None:
                existing_place_ids = set()
            if existing_business_keys is None:
                existing_business_keys = set()
            
            logger.info(f"Starting search: Target {max_results} businesses, checking against {len(existing_place_ids)} existing place_ids and {len(existing_business_keys)} existing business keys")
            
            # Continue searching until we have enough non-duplicate businesses
            while len(businesses) < max_results and page_count < max_pages:
                # Process current page results
                if 'results' in places_result and places_result['results']:
                    for place in places_result['results']:
                        if len(businesses) >= max_results:
                            break
                        
                        place_id = place.get('place_id')
                        place_name = place.get('name', 'Unknown')
                        place_address = place.get('formatted_address', 'Unknown')
                        
                        # Step 3: Check for duplicates - check against previous search results first
                        # If duplicate found, skip this business and continue searching (count effectively decreases by 1)
                        is_duplicate = False
                        
                        if place_id:
                            if place_id in existing_place_ids:
                                logger.info(f"⏭️  Duplicate found in previous search: {place_name} - skipping and searching for another business...")
                                print(f"⏭️  Duplicate found in previous search: {place_name} - skipping and continuing search...")
                                is_duplicate = True
                            elif place_id in seen_place_ids:
                                logger.debug(f"Skipping duplicate (place_id in current search): {place_name}")
                                is_duplicate = True
                            else:
                                seen_place_ids.add(place_id)
                        else:
                            # For businesses without place_id, use name+address as fallback
                            business_key = f"{place_name.lower().strip()}|{place_address.lower().strip()}"
                            if business_key in existing_business_keys:
                                logger.info(f"⏭️  Duplicate found in previous search: {place_name} - skipping and searching for another business...")
                                print(f"⏭️  Duplicate found in previous search: {place_name} - skipping and continuing search...")
                                is_duplicate = True
                            elif business_key in seen_business_keys:
                                logger.debug(f"Skipping duplicate (name+location in current search): {place_name}")
                                is_duplicate = True
                            else:
                                seen_business_keys.add(business_key)
                        
                        # If duplicate, skip this business and continue searching
                        # The loop will continue until we have max_results non-duplicate businesses
                        if is_duplicate:
                            continue
                            
                        business = {
                            'name': place_name,
                            'location': place_address,
                            'website': None,
                            'place_id': place_id
                        }
                        
                        # Get detailed information including website
                        if business['place_id']:
                            try:
                                details = self.gmaps.place(
                                    place_id=business['place_id'],
                                    fields=['website', 'name', 'formatted_address', 'international_phone_number']
                                )
                                if 'result' in details:
                                    result = details['result']
                                    business['website'] = result.get('website')
                                    business['phone'] = result.get('international_phone_number')
                            except Exception as e:
                                logger.warning(f"Could not fetch details for {business['name']}: {e}")
                        
                        # Skip if website required but not found
                        if website_required and not business['website']:
                            continue
                        
                        businesses.append(business)
                
                # Check for next page token
                next_page_token = places_result.get('next_page_token')
                
                if next_page_token and len(businesses) < max_results:
                    # Wait a few seconds (Google requires a delay between page requests)
                    time.sleep(2)
                    
                    # Get next page
                    try:
                        places_result = self.gmaps.places(query=query, page_token=next_page_token)
                        page_count += 1
                        logger.info(f"Fetching page {page_count + 1}, current results: {len(businesses)}")
                        
                        # Check for errors in subsequent pages
                        if 'status' in places_result:
                            status = places_result['status']
                            if status != 'OK':
                                logger.warning(f"Error fetching next page: {status}")
                                break
                    except Exception as e:
                        logger.warning(f"Error fetching next page: {e}")
                        break
                else:
                    # No more pages available
                    break
                    
            if page_count == 0 and 'results' not in places_result:
                logger.info(f"No results found for query: {query}")
            else:
                logger.info(f"✅ Search complete: Found {len(businesses)} non-duplicate businesses from {page_count + 1} page(s) (target was {max_results})")
                        
        except Exception as e:
            error_msg = str(e)
            error_lower = error_msg.lower()
            
            # Check for various API-related errors
            if any(term in error_lower for term in ['request_denied', 'api key', 'not enabled', 
                                                     'legacyapi', 'permission denied', 'not activated']):
                logger.error(f"\n{'='*60}")
                logger.error("⚠️  PLACES API NOT ENABLED!")
                logger.error(f"{'='*60}")
                logger.error("Your API key exists but Places API is not enabled.")
                logger.error("\n🔧 To fix this:")
                logger.error("1. Go to: https://console.cloud.google.com/google/maps-apis")
                logger.error("2. Select your project")
                logger.error("3. Click 'Enable APIs and Services' (or 'APIs & Services' > 'Library')")
                logger.error("4. Search for 'Places API' and click ENABLE")
                logger.error("5. Also enable 'Places API (New)' if available")
                logger.error("6. Wait 2-5 minutes for activation")
                logger.error("7. Make sure billing is enabled (free tier: $200/month credit)")
                logger.error(f"{'='*60}\n")
            elif 'over_query_limit' in error_lower or 'quota' in error_lower:
                logger.error(f"⚠️  API Quota Exceeded: {e}")
                logger.error("Check your billing and quota in Google Cloud Console")
            else:
                logger.error(f"Google Maps API error: {e}")
                logger.error("Full error details above. Check API key and enable Places API.")
            
        return businesses
    
    def _search_fallback(
        self, 
        query: str, 
        max_results: int, 
        website_required: bool,
        existing_place_ids: set = None,
        existing_business_keys: set = None
    ) -> List[Dict]:
        """
        Fallback search method when API is unavailable
        Returns sample structure - in production, could use alternative APIs
        """
        logger.warning("Using fallback discovery method. Results may be limited.")
        # In a real implementation, you could:
        # - Use alternative APIs (Yelp, Bing Places, etc.)
        # - Web scrape business directories
        # - Use structured data from search engines
        
        return []
    
    def validate_website(self, url: str) -> bool:
        """Validate that a URL is accessible"""
        
        if not url or not validators.url(url):
            return False
        
        try:
            response = requests.head(
                url, 
                timeout=config.DEFAULT_TIMEOUT,
                allow_redirects=True,
                headers={'User-Agent': config.USER_AGENT}
            )
            return response.status_code < 400
        except Exception:
            return False

