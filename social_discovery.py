"""
Social Media Discovery Module
Detects and extracts social media profile links from websites
"""
import re
from bs4 import BeautifulSoup
from typing import Dict, Optional
import logging
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SocialMediaDiscovery:
    """Discover social media profiles from business websites"""
    
    # Social media URL patterns
    SOCIAL_PATTERNS = {
        'instagram': [
            r'instagram\.com/([a-zA-Z0-9_.]+)',
            r'instagr\.am/([a-zA-Z0-9_.]+)'
        ],
        'facebook': [
            r'facebook\.com/([a-zA-Z0-9_.]+)',
            r'fb\.com/([a-zA-Z0-9_.]+)'
        ],
        'linkedin': [
            r'linkedin\.com/(?:company|in|pub)/([a-zA-Z0-9_.-]+)'
        ],
        'twitter': [
            r'(?:twitter|x)\.com/([a-zA-Z0-9_]+)'
        ],
        'youtube': [
            r'youtube\.com/(?:channel|c|user|@)/([a-zA-Z0-9_.-]+)',
            r'youtu\.be/([a-zA-Z0-9_.-]+)'
        ]
    }
    
    def __init__(self):
        self.base_url = None
    
    def discover_socials(self, website_url: str, html_content: str = None) -> Dict[str, Optional[str]]:
        """
        Discover social media profiles from a website
        
        Args:
            website_url: Base URL of the website
            html_content: HTML content of the page (optional, will fetch if not provided)
            
        Returns:
            Dictionary with social media links
        """
        socials = {
            'instagram': None,
            'facebook': None,
            'linkedin': None,
            'twitter': None,
            'youtube': None
        }
        
        try:
            self.base_url = website_url
            
            # Parse HTML
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
            else:
                soup = self._fetch_and_parse(website_url)
                if not soup:
                    return socials
            
            html_str = str(soup)
            
            # Search for social links in HTML
            socials.update(self._extract_from_html(html_str))
            
            # Also check footer and header sections specifically
            footer = soup.find('footer')
            header = soup.find('header')
            
            if footer:
                socials.update(self._extract_from_html(str(footer)))
            if header:
                socials.update(self._extract_from_html(str(header)))
            
        except Exception as e:
            logger.error(f"Error discovering socials for {website_url}: {e}")
        
        return socials
    
    def _fetch_and_parse(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        import requests
        import config
        
        try:
            response = requests.get(
                url, 
                timeout=config.DEFAULT_TIMEOUT,
                headers={'User-Agent': config.USER_AGENT}
            )
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.warning(f"Could not fetch {url}: {e}")
            return None
    
    def _extract_from_html(self, html: str) -> Dict[str, Optional[str]]:
        """Extract social media links from HTML content"""
        found_socials = {
            'instagram': None,
            'facebook': None,
            'linkedin': None,
            'twitter': None,
            'youtube': None
        }
        
        # Check each social media platform
        for platform, patterns in self.SOCIAL_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    username = matches[0]
                    # Construct full URL
                    url = self._construct_social_url(platform, username)
                    if url:
                        found_socials[platform] = url
                        break  # Take first match
        
        # Also check for direct links in anchor tags
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            for platform, patterns in self.SOCIAL_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, href, re.IGNORECASE):
                        # Already found, but update if this is a better formatted URL
                        if not found_socials[platform] or 'https://' in link['href']:
                            found_socials[platform] = link['href'] if link['href'].startswith('http') else urljoin(self.base_url, link['href'])
                        break
        
        return found_socials
    
    def _construct_social_url(self, platform: str, username: str) -> Optional[str]:
        """Construct full social media URL from username"""
        base_urls = {
            'instagram': f'https://instagram.com/{username}',
            'facebook': f'https://facebook.com/{username}',
            'linkedin': f'https://linkedin.com/company/{username}',  # Default to company
            'twitter': f'https://twitter.com/{username}',
            'youtube': f'https://youtube.com/{username}'
        }
        
        return base_urls.get(platform)


