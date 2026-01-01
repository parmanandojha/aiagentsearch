"""
Output Formatter Module
Formats the final JSON output with summary and business details
"""
from typing import List, Dict
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutputFormatter:
    """Format audit results into structured JSON output"""
    
    def format_output(
        self,
        industry: str,
        location: str,
        businesses: List[Dict]
    ) -> Dict:
        """
        Format complete audit results into final JSON structure
        
        Args:
            industry: Industry searched
            location: Location searched
            businesses: List of business audit results
            
        Returns:
            Formatted JSON dictionary
        """
        # Calculate summary statistics
        total_businesses = len(businesses)
        
        # Count poor websites (score < 4.0)
        poor_websites = sum(
            1 for biz in businesses 
            if biz.get('website_score', 0) < 4.0
        )
        poor_websites_percentage = (
            (poor_websites / total_businesses * 100) 
            if total_businesses > 0 else 0
        )
        
        # Find top opportunities (low scores = high opportunity for improvement)
        sorted_businesses = sorted(
            businesses,
            key=lambda x: x.get('website_score', 10)
        )
        top_opportunities = [
            {
                'name': biz['name'],
                'website': biz.get('website', ''),
                'score': biz.get('website_score', 0),
                'opportunity_level': biz.get('opportunity_level', '')
            }
            for biz in sorted_businesses[:5]  # Top 5 opportunities
        ]
        
        # Build summary
        summary = {
            'industry': industry,
            'location': location,
            'total_businesses': total_businesses,
            'poor_websites_percentage': round(poor_websites_percentage, 2),
            'top_opportunities': top_opportunities
        }
        
        # Format businesses (ensure all fields are present)
        formatted_businesses = []
        for biz in businesses:
            formatted_biz = self._format_business(biz)
            formatted_businesses.append(formatted_biz)
        
        return {
            'summary': summary,
            'businesses': formatted_businesses
        }
    
    def _format_business(self, business: Dict) -> Dict:
        """
        Format a single business entry ensuring all required fields
        
        Args:
            business: Business dictionary with audit results
            
        Returns:
            Formatted business dictionary
        """
        # Default values
        default_contact = {
            'phone': None,
            'email': None,
            'contact_form': None
        }
        
        default_socials = {
            'instagram': None,
            'facebook': None,
            'linkedin': None,
            'twitter': None,
            'youtube': None
        }
        
        default_tech = {
            'cms': 'Not Detected',
            'frontend': 'Not Detected',
            'analytics': 'None Detected'
        }
        
        # Format contact info
        contact = business.get('contact', {})
        formatted_contact = {
            'phone': contact.get('phone') or None,
            'email': contact.get('email') or None,
            'contact_form': contact.get('contact_form') or None
        }
        
        # Format socials
        socials = business.get('socials', {})
        formatted_socials = {
            'instagram': socials.get('instagram') or None,
            'facebook': socials.get('facebook') or None,
            'linkedin': socials.get('linkedin') or None,
            'twitter': socials.get('twitter') or None,
            'youtube': socials.get('youtube') or None
        }
        
        # Format tech stack
        tech_stack = business.get('tech_stack', {})
        analytics = tech_stack.get('analytics', [])
        if isinstance(analytics, list):
            analytics = analytics if analytics else 'None Detected'
        
        formatted_tech = {
            'cms': tech_stack.get('cms', 'Not Detected'),
            'frontend': tech_stack.get('frontend', 'Not Detected'),
            'analytics': analytics
        }
        
        # Format issues
        issues = business.get('issues', [])
        if not isinstance(issues, list):
            issues = []
        
        return {
            'name': business.get('name', 'Unknown'),
            'website': business.get('website') or None,
            'location': business.get('location', 'Unknown'),
            'contact': formatted_contact,
            'socials': formatted_socials,
            'tech_stack': formatted_tech,
            'issues': issues,
            'website_score': business.get('website_score', 0),
            'opportunity_level': business.get('opportunity_level', 'Unknown')
        }
    
    def to_json(self, data: Dict, indent: int = 2) -> str:
        """
        Convert dictionary to JSON string
        
        Args:
            data: Dictionary to convert
            indent: JSON indentation level
            
        Returns:
            JSON string
        """
        return json.dumps(data, indent=indent, ensure_ascii=False)


