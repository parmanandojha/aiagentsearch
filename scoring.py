"""
Scoring Module
Calculates website scores and determines opportunity levels
"""
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import config


class WebsiteScorer:
    """Score websites and determine opportunity levels"""
    
    def __init__(self):
        self.thresholds = config.SCORE_THRESHOLDS
    
    def calculate_score(self, audit_result: Dict) -> float:
        """
        Calculate overall website score (0-10)
        
        Args:
            audit_result: Dictionary containing audit results
            
        Returns:
            Score between 0 and 10
        """
        score = 10.0
        
        ux = audit_result.get('ux_design', {})
        content = audit_result.get('content', {})
        issues = audit_result.get('issues', [])
        tech = audit_result.get('tech_stack', {})
        performance = audit_result.get('performance', {})
        
        # UX/Design deductions
        if not ux.get('mobile_responsive', False):
            score -= 1.5
        if ux.get('navigation_clarity') == 'Poor':
            score -= 1.0
        if not ux.get('cta_present', False):
            score -= 0.5
        if ux.get('visual_modernity') == 'Outdated':
            score -= 1.0
        
        # Content deductions
        if not content.get('value_proposition', False):
            score -= 0.5
        if not content.get('services_listed', False):
            score -= 0.5
        missing_pages = content.get('missing_pages', [])
        score -= len(missing_pages) * 0.3
        
        # Technical issues deductions
        issue_penalties = {
            'Missing SSL': 2.0,
            'Missing meta title': 0.5,
            'Missing meta description': 0.5,
            'Missing H1 tag': 0.5,
            'Broken links': 1.0,
            'Large page size': 0.5,
            'Many images missing alt text': 0.5
        }
        
        for issue in issues:
            for issue_type, penalty in issue_penalties.items():
                if issue_type.lower() in issue.lower():
                    score -= penalty
                    break
        
        # Performance deductions
        load_time = performance.get('load_time', 0)
        if load_time > 3:
            score -= 1.0
        elif load_time > 5:
            score -= 2.0
        
        # Bonus points for modern tech stack
        cms = tech.get('cms', '')
        if 'Custom' in cms or cms in ['Webflow', 'Shopify']:
            score += 0.5
        
        # Ensure score is between 0 and 10
        score = max(0.0, min(10.0, score))
        
        return round(score, 2)
    
    def determine_opportunity_level(self, score: float) -> str:
        """
        Determine opportunity level based on score
        
        Args:
            score: Website score (0-10)
            
        Returns:
            Opportunity level string
        """
        if score >= self.thresholds['high_potential']:
            return "High Potential"
        elif score < self.thresholds['needs_redesign']:
            return "Needs Redesign"
        else:
            return "Digitally Mature"
    
    def score_business(
        self, 
        audit_result: Dict, 
        contact_info: Dict, 
        social_info: Dict
    ) -> Dict:
        """
        Generate complete scoring for a business
        
        Args:
            audit_result: Website audit results
            contact_info: Contact information
            social_info: Social media information
            
        Returns:
            Dictionary with website_score and opportunity_level
        """
        website_score = self.calculate_score(audit_result)
        opportunity_level = self.determine_opportunity_level(website_score)
        
        return {
            'website_score': website_score,
            'opportunity_level': opportunity_level
        }


