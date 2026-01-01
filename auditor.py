"""
Website Audit Module
Analyzes websites for UX, content, tech stack, and technical issues
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import config
import logging
from urllib.parse import urljoin, urlparse
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebsiteAuditor:
    """Audit business websites for various metrics"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
    
    def audit_website(self, website_url: str) -> Dict:
        """
        Perform comprehensive website audit
        
        Args:
            website_url: URL of the website to audit
            
        Returns:
            Dictionary containing audit results
        """
        audit_result = {
            'ux_design': {},
            'content': {},
            'tech_stack': {},
            'issues': [],
            'performance': {}
        }
        
        try:
            # Fetch the page
            response = self._fetch_page(website_url)
            if not response:
                audit_result['issues'].append('Website not accessible')
                return audit_result
            
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Measure load time
            start_time = time.time()
            load_time = response.elapsed.total_seconds()
            audit_result['performance']['load_time'] = load_time
            
            # UX/Design Analysis
            audit_result['ux_design'] = self._audit_ux_design(soup, html_content, website_url)
            
            # Content Analysis
            audit_result['content'] = self._audit_content(soup, html_content)
            
            # Tech Stack Detection
            audit_result['tech_stack'] = self._detect_tech_stack(soup, html_content, response.headers)
            
            # Technical Issues
            audit_result['issues'] = self._check_technical_issues(
                soup, html_content, website_url, response
            )
            
        except Exception as e:
            logger.error(f"Error auditing {website_url}: {e}")
            audit_result['issues'].append(f'Audit error: {str(e)}')
        
        return audit_result
    
    def _fetch_page(self, url: str) -> Optional[requests.Response]:
        """Fetch a web page with error handling"""
        try:
            response = self.session.get(url, timeout=config.DEFAULT_TIMEOUT)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.warning(f"Could not fetch {url}: {e}")
            return None
    
    def _audit_ux_design(
        self, 
        soup: BeautifulSoup, 
        html: str, 
        base_url: str
    ) -> Dict:
        """Analyze UX and design aspects"""
        ux = {
            'mobile_responsive': False,
            'navigation_clarity': 'Unknown',
            'visual_modernity': 'Unknown',
            'cta_present': False
        }
        
        # Check for mobile responsiveness
        meta_viewport = soup.find('meta', attrs={'name': 'viewport'})
        ux['mobile_responsive'] = meta_viewport is not None
        
        # Check for responsive CSS
        if not ux['mobile_responsive']:
            links = soup.find_all('link', rel='stylesheet')
            for link in links:
                href = link.get('href', '')
                media = link.get('media', '')
                if 'media' in str(link) or 'responsive' in href.lower():
                    ux['mobile_responsive'] = True
                    break
        
        # Check navigation clarity (look for nav element or menu)
        nav = soup.find('nav') or soup.find(class_=re.compile(r'nav|menu', re.I))
        ux['navigation_clarity'] = 'Good' if nav else 'Poor'
        
        # Check for CTA buttons/links
        cta_keywords = [
            'contact us', 'get started', 'sign up', 'book now', 
            'call now', 'learn more', 'free trial', 'buy now'
        ]
        page_text = soup.get_text().lower()
        links_text = [a.get_text().lower() for a in soup.find_all('a')]
        
        ux['cta_present'] = any(
            keyword in page_text or keyword in ' '.join(links_text)
            for keyword in cta_keywords
        )
        
        # Visual modernity (basic heuristic)
        # Check for modern CSS frameworks, modern HTML5 elements
        modern_indicators = [
            soup.find('section'), soup.find('article'), soup.find('header'),
            soup.find('footer'), soup.find('main')
        ]
        modern_css = bool(re.search(r'(bootstrap|tailwind|material|foundation)', html, re.I))
        
        if modern_css or any(modern_indicators):
            ux['visual_modernity'] = 'Modern'
        elif soup.find('table') and not soup.find('div'):  # Old table-based layout
            ux['visual_modernity'] = 'Outdated'
        else:
            ux['visual_modernity'] = 'Average'
        
        return ux
    
    def _audit_content(self, soup: BeautifulSoup, html: str) -> Dict:
        """Analyze content aspects"""
        content = {
            'value_proposition': False,
            'services_listed': False,
            'missing_pages': []
        }
        
        page_text = soup.get_text().lower()
        
        # Check for value proposition keywords
        value_prop_keywords = [
            'best', 'quality', 'expert', 'leading', 'trusted',
            'experience', 'professional', 'award', 'guarantee'
        ]
        content['value_proposition'] = any(keyword in page_text for keyword in value_prop_keywords)
        
        # Check if services are listed
        service_indicators = [
            'services', 'what we do', 'our services', 'offerings',
            'products', 'solutions'
        ]
        content['services_listed'] = any(
            indicator in page_text or soup.find(id=re.compile(indicator, re.I))
            for indicator in service_indicators
        )
        
        # Check for common pages (check links)
        required_pages = ['about', 'contact', 'privacy']
        links_href = [a.get('href', '').lower() for a in soup.find_all('a', href=True)]
        
        for page in required_pages:
            if not any(page in href for href in links_href):
                content['missing_pages'].append(page.capitalize())
        
        return content
    
    def _detect_tech_stack(
        self, 
        soup: BeautifulSoup, 
        html: str, 
        headers: Dict
    ) -> Dict:
        """Detect technology stack"""
        tech = {
            'cms': 'Not Detected',
            'frontend': 'Not Detected',
            'analytics': []
        }
        
        html_lower = html.lower()
        
        # Detect CMS
        cms_patterns = {
            'WordPress': [
                r'wp-content', r'wordpress', r'/wp-includes/', r'wp-json'
            ],
            'Shopify': [
                r'shopify', r'shopifycdn', r'cdn\.shopify\.com'
            ],
            'Webflow': [
                r'webflow', r'\.webflow\.io', r'webflowcdn'
            ],
            'Wix': [
                r'wix\.com', r'wixpress', r'wixstatic'
            ],
            'Squarespace': [
                r'squarespace', r'ssqs\.com'
            ],
            'Drupal': [
                r'drupal', r'/sites/default/'
            ],
            'Joomla': [
                r'joomla', r'/components/'
            ]
        }
        
        for cms_name, patterns in cms_patterns.items():
            if any(re.search(pattern, html_lower) for pattern in patterns):
                tech['cms'] = cms_name
                break
        
        # If no CMS detected, check for custom frameworks
        if tech['cms'] == 'Not Detected':
            if re.search(r'react|reactjs', html_lower):
                tech['cms'] = 'Custom (React)'
            elif re.search(r'vue|vuejs', html_lower):
                tech['cms'] = 'Custom (Vue)'
            elif re.search(r'angular', html_lower):
                tech['cms'] = 'Custom (Angular)'
            elif re.search(r'next\.js|nextjs', html_lower):
                tech['cms'] = 'Custom (Next.js)'
        
        # Detect frontend framework
        frontend_patterns = {
            'React': r'react|reactjs',
            'Vue': r'vue\.js|vuejs',
            'Angular': r'angular',
            'jQuery': r'jquery',
            'Bootstrap': r'bootstrap',
            'Tailwind': r'tailwindcss'
        }
        
        for framework, pattern in frontend_patterns.items():
            if re.search(pattern, html_lower):
                tech['frontend'] = framework
                break
        
        # Detect analytics
        analytics_patterns = {
            'Google Analytics': [r'google-analytics\.com', r'gtag', r'ga\(', r'analytics\.js'],
            'Google Tag Manager': [r'googletagmanager\.com', r'GTM-'],
            'Facebook Pixel': [r'facebook\.net', r'fbq'],
            'Hotjar': [r'hotjar\.com'],
            'Mixpanel': [r'mixpanel\.com']
        }
        
        for analytics_name, patterns in analytics_patterns.items():
            if any(re.search(pattern, html_lower) for pattern in patterns):
                tech['analytics'].append(analytics_name)
        
        if not tech['analytics']:
            tech['analytics'] = 'None Detected'
        
        return tech
    
    def _check_technical_issues(
        self, 
        soup: BeautifulSoup, 
        html: str, 
        base_url: str,
        response: requests.Response
    ) -> List[str]:
        """Check for technical issues"""
        issues = []
        
        # Check SSL (HTTPS)
        if not base_url.startswith('https://'):
            issues.append('Missing SSL (not using HTTPS)')
        
        # Check meta tags (SEO)
        title_tag = soup.find('title')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        
        if not title_tag or not title_tag.get_text().strip():
            issues.append('Missing meta title')
        
        if not meta_description:
            issues.append('Missing meta description')
        
        # Check for H1
        h1_tags = soup.find_all('h1')
        if not h1_tags:
            issues.append('Missing H1 tag')
        elif len(h1_tags) > 1:
            issues.append('Multiple H1 tags (SEO issue)')
        
        # Check for broken links (sample a few internal links)
        internal_links = self._get_internal_links(soup, base_url)
        broken_count = 0
        checked = 0
        
        for link in internal_links[:10]:  # Check first 10 internal links
            checked += 1
            try:
                link_response = self.session.head(link, timeout=5, allow_redirects=True)
                if link_response.status_code >= 400:
                    broken_count += 1
            except:
                broken_count += 1
        
        if broken_count > 0:
            issues.append(f'Broken links detected ({broken_count}/{checked} checked)')
        
        # Check for performance issues (basic)
        # Large page size
        page_size_mb = len(html.encode('utf-8')) / (1024 * 1024)
        if page_size_mb > 5:
            issues.append(f'Large page size ({page_size_mb:.1f}MB)')
        
        # Check for images without alt text
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        if len(images_without_alt) > len(images) * 0.3:  # More than 30% without alt
            issues.append('Many images missing alt text (accessibility/SEO issue)')
        
        return issues
    
    def _get_internal_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Get list of internal links from the page"""
        internal_links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            
            if parsed.netloc == base_domain and parsed.scheme in ['http', 'https']:
                internal_links.append(full_url)
        
        return list(set(internal_links))  # Remove duplicates


