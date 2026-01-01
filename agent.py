"""
Main Business Discovery Agent
Orchestrates all modules to discover and audit businesses
"""
import logging
from typing import Dict, Optional
import time

from discovery import BusinessDiscovery
from contact_extractor import ContactExtractor
from social_discovery import SocialMediaDiscovery
from auditor import WebsiteAuditor
from scoring import WebsiteScorer
from formatter import OutputFormatter
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BusinessDiscoveryAgent:
    """
    Main agent that orchestrates business discovery and website auditing
    """
    
    def __init__(self, google_maps_api_key: Optional[str] = None):
        """
        Initialize the agent with all required modules
        
        Args:
            google_maps_api_key: Optional Google Maps API key
        """
        self.discovery = BusinessDiscovery(api_key=google_maps_api_key)
        self.contact_extractor = ContactExtractor()
        self.social_discovery = SocialMediaDiscovery()
        self.auditor = WebsiteAuditor()
        self.scorer = WebsiteScorer()
        self.formatter = OutputFormatter()
        
        logger.info("Business Discovery Agent initialized")
    
    def run_streaming(
        self,
        industry: str,
        location: str,
        max_results: int = config.DEFAULT_MAX_RESULTS,
        website_required: bool = config.DEFAULT_WEBSITE_REQUIRED,
        callback=None
    ) -> Dict:
        """
        Run the agent with streaming support - calls callback for each business processed
        
        Args:
            industry: Industry/type of business to search for
            location: Geographic location to search in
            max_results: Maximum number of businesses to process
            website_required: Only process businesses with websites
            callback: Function to call with (business, index, total) for each processed business
            
        Returns:
            Complete audit report as dictionary
        """
        logger.info(f"Starting streaming discovery for: {industry} in {location}")
        
        # Step 1: Discover businesses
        logger.info("Step 1: Discovering businesses...")
        businesses = self.discovery.search_businesses(
            industry=industry,
            location=location,
            max_results=max_results,
            website_required=website_required,
            existing_place_ids=getattr(self, '_existing_place_ids', set()),
            existing_business_keys=getattr(self, '_existing_business_keys', set())
        )
        
        if not businesses:
            logger.warning("No businesses found. Returning empty results.")
            return self.formatter.format_output(industry, location, [])
        
        logger.info(f"Found {len(businesses)} businesses")
        
        # Step 2: Process each business with callback
        processed_businesses = []
        
        for idx, business in enumerate(businesses, 1):
            logger.info(f"Processing business {idx}/{len(businesses)}: {business.get('name', 'Unknown')}")
            
            try:
                processed_biz = self._process_business(business)
                processed_businesses.append(processed_biz)
                
                # Call callback if provided (for streaming)
                if callback:
                    callback(processed_biz, idx, len(businesses))
                
                # Rate limiting - be respectful
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing {business.get('name')}: {e}")
                # Add business with minimal info if processing fails
                processed_biz = {
                    'name': business.get('name', 'Unknown'),
                    'website': business.get('website'),
                    'location': business.get('location', 'Unknown'),
                    'contact': {},
                    'socials': {},
                    'tech_stack': {},
                    'issues': [f'Processing error: {str(e)}'],
                    'website_score': 0,
                    'opportunity_level': 'Unknown'
                }
                processed_businesses.append(processed_biz)
                
                # Call callback even for errors
                if callback:
                    callback(processed_biz, idx, len(businesses))
        
        # Step 3: Format output
        logger.info("Formatting output...")
        output = self.formatter.format_output(
            industry=industry,
            location=location,
            businesses=processed_businesses
        )
        
        logger.info("Audit complete!")
        return output
    
    def run(
        self,
        industry: str,
        location: str,
        max_results: int = config.DEFAULT_MAX_RESULTS,
        website_required: bool = config.DEFAULT_WEBSITE_REQUIRED
    ) -> Dict:
        """
        Run the complete business discovery and audit process
        
        Args:
            industry: Industry/type of business to search for
            location: Geographic location to search in
            max_results: Maximum number of businesses to process
            website_required: Only process businesses with websites
            
        Returns:
            Complete audit report as dictionary
        """
        logger.info(f"Starting discovery for: {industry} in {location}")
        
        # Step 1: Discover businesses
        logger.info("Step 1: Discovering businesses...")
        businesses = self.discovery.search_businesses(
            industry=industry,
            location=location,
            max_results=max_results,
            website_required=website_required,
            existing_place_ids=getattr(self, '_existing_place_ids', set()),
            existing_business_keys=getattr(self, '_existing_business_keys', set())
        )
        
        if not businesses:
            logger.warning("No businesses found. Returning empty results.")
            return self.formatter.format_output(industry, location, [])
        
        logger.info(f"Found {len(businesses)} businesses")
        
        # Step 2: Process each business
        processed_businesses = []
        
        for idx, business in enumerate(businesses, 1):
            logger.info(f"Processing business {idx}/{len(businesses)}: {business.get('name', 'Unknown')}")
            
            try:
                processed_biz = self._process_business(business)
                processed_businesses.append(processed_biz)
                
                # Rate limiting - be respectful
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing {business.get('name')}: {e}")
                # Add business with minimal info if processing fails
                processed_biz = {
                    'name': business.get('name', 'Unknown'),
                    'website': business.get('website'),
                    'location': business.get('location', 'Unknown'),
                    'contact': {},
                    'socials': {},
                    'tech_stack': {},
                    'issues': [f'Processing error: {str(e)}'],
                    'website_score': 0,
                    'opportunity_level': 'Unknown'
                }
                processed_businesses.append(processed_biz)
        
        # Step 3: Format output
        logger.info("Formatting output...")
        output = self.formatter.format_output(
            industry=industry,
            location=location,
            businesses=processed_businesses
        )
        
        logger.info("Audit complete!")
        return output
    
    def _process_business(self, business: Dict) -> Dict:
        """
        Process a single business: extract contacts, socials, audit, and score
        
        Args:
            business: Business dictionary with name, website, location
            
        Returns:
            Complete business dictionary with all audit information
        """
        website = business.get('website')
        business_name = business.get('name', 'Unknown')
        
        # Initialize result structure
        result = {
            'name': business_name,
            'website': website,
            'location': business.get('location', 'Unknown'),
            'contact': {},
            'socials': {},
            'tech_stack': {},
            'issues': [],
            'website_score': 0,
            'opportunity_level': 'Unknown'
        }
        
        # If no website, return early with minimal info
        if not website:
            logger.warning(f"No website for {business_name}")
            return result
        
        # Validate website URL
        if not self.discovery.validate_website(website):
            result['issues'].append('Website not accessible')
            return result
        
        try:
            # Extract contact information
            logger.debug(f"Extracting contacts from {website}")
            result['contact'] = self.contact_extractor.extract_contacts(website)
            
            # Discover social media
            logger.debug(f"Discovering social media for {website}")
            result['socials'] = self.social_discovery.discover_socials(website)
            
            # Audit website
            logger.debug(f"Auditing website {website}")
            audit_result = self.auditor.audit_website(website)
            
            # Extract audit components
            result['tech_stack'] = audit_result.get('tech_stack', {})
            result['issues'] = audit_result.get('issues', [])
            
            # Score the website
            logger.debug(f"Scoring website {website}")
            scoring_result = self.scorer.score_business(
                audit_result=audit_result,
                contact_info=result['contact'],
                social_info=result['socials']
            )
            
            result['website_score'] = scoring_result['website_score']
            result['opportunity_level'] = scoring_result['opportunity_level']
            
        except Exception as e:
            logger.error(f"Error processing website {website}: {e}")
            result['issues'].append(f'Processing error: {str(e)}')
        
        return result


def main():
    """
    Main entry point for command-line usage
    """
    import argparse
    import json
    import sys
    
    parser = argparse.ArgumentParser(
        description='Business Discovery and Website Audit Agent'
    )
    parser.add_argument('--industry', type=str, required=True,
                       help='Industry/business type (e.g., "restaurants", "dentists")')
    parser.add_argument('--location', type=str, required=True,
                       help='Geographic location (e.g., "New York, NY")')
    parser.add_argument('--max-results', type=int, default=config.DEFAULT_MAX_RESULTS,
                       help=f'Maximum number of results (default: {config.DEFAULT_MAX_RESULTS})')
    parser.add_argument('--website-required', action='store_true',
                       help='Only return businesses with websites')
    parser.add_argument('--api-key', type=str, default=None,
                       help='Google Maps API key (or set GOOGLE_MAPS_API_KEY in .env)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output file path (default: print to stdout)')
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = BusinessDiscoveryAgent(google_maps_api_key=args.api_key)
    
    # Run audit
    try:
        results = agent.run(
            industry=args.industry,
            location=args.location,
            max_results=args.max_results,
            website_required=args.website_required
        )
        
        # Format as JSON
        json_output = agent.formatter.to_json(results)
        
        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"Results saved to {args.output}")
        else:
            print(json_output)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

