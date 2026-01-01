"""
Contact Information Extraction Module
Extracts phone numbers, emails, and contact forms from websites
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import config
import logging
from urllib.parse import urljoin, urlparse
import phonenumbers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContactExtractor:
    """Extract contact information from business websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
    
    def extract_contacts(self, website_url: str) -> Dict[str, Optional[str]]:
        """
        Extract all contact information from a website
        
        Args:
            website_url: URL of the business website
            
        Returns:
            Dictionary with phone, email, contact_form, whatsapp
        """
        contacts = {
            'phone': None,
            'email': None,
            'contact_form': None,
            'whatsapp': None
        }
        
        try:
            response = self._fetch_page(website_url)
            if not response:
                return contacts
            
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            html_content = str(response.text)
            
            # Extract phone
            contacts['phone'] = self._extract_phone(soup, page_text, website_url)
            
            # Extract email
            contacts['email'] = self._extract_email(soup, page_text)
            
            # Extract contact form URL
            contacts['contact_form'] = self._extract_contact_form(soup, website_url)
            
            # Extract WhatsApp link
            contacts['whatsapp'] = self._extract_whatsapp(soup, html_content)
            
        except Exception as e:
            logger.error(f"Error extracting contacts from {website_url}: {e}")
        
        return contacts
    
    def _fetch_page(self, url: str) -> Optional[requests.Response]:
        """Fetch a web page with error handling"""
        try:
            response = self.session.get(url, timeout=config.DEFAULT_TIMEOUT)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.warning(f"Could not fetch {url}: {e}")
            return None
    
    def _extract_phone(
        self, 
        soup: BeautifulSoup, 
        text: str, 
        base_url: str
    ) -> Optional[str]:
        """Extract phone number from page"""
        # Patterns for phone numbers
        patterns = [
            r'\+?1?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
            r'\+?[\d\s\-\(\)]{10,}',  # Generic
        ]
        
        # Check links with tel: protocol
        tel_links = soup.find_all('a', href=re.compile(r'^tel:'))
        if tel_links:
            phone = tel_links[0]['href'].replace('tel:', '').strip()
            return self._normalize_phone(phone)
        
        # Search in text content
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                phone = self._normalize_phone(matches[0])
                if phone:
                    return phone
        
        return None
    
    def _normalize_phone(self, phone: str) -> Optional[str]:
        """Normalize and validate phone number"""
        # Clean up the phone number
        phone = re.sub(r'[^\d\+]', '', phone)
        
        if len(phone) < 10:
            return None
        
        # Try to parse with phonenumbers library
        try:
            # Try different country codes
            for country in ['US', 'GB', 'CA', 'AU']:
                try:
                    parsed = phonenumbers.parse(phone, country)
                    if phonenumbers.is_valid_number(parsed):
                        return phonenumbers.format_number(
                            parsed, 
                            phonenumbers.PhoneNumberFormat.INTERNATIONAL
                        )
                except:
                    continue
        except:
            pass
        
        # Fallback: return cleaned phone if it looks valid
        if phone.startswith('+') or (phone.replace('+', '').isdigit() and len(phone.replace('+', '')) >= 10):
            return phone if phone.startswith('+') else f"+{phone}"
        
        return None
    
    def _extract_email(self, soup: BeautifulSoup, text: str) -> Optional[str]:
        """Extract email address from page"""
        # Email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Check mailto: links first
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
        if mailto_links:
            email = mailto_links[0]['href'].replace('mailto:', '').split('?')[0].strip()
            if self._is_valid_email(email):
                return email
        
        # Search in text
        matches = re.findall(email_pattern, text)
        for match in matches:
            # Filter out common false positives
            if not any(skip in match.lower() for skip in ['example.com', 'sentry.io', 'wixpress.com']):
                if self._is_valid_email(match):
                    return match
        
        return None
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _extract_contact_form(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Find contact form URL"""
        # Look for contact form links
        contact_keywords = ['contact', 'get-in-touch', 'reach-out', 'message-us']
        
        # Check links
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            text = link.get_text().lower()
            
            if any(keyword in href or keyword in text for keyword in contact_keywords):
                url = urljoin(base_url, link['href'])
                return url
        
        # Check forms
        forms = soup.find_all('form')
        if forms:
            for form in forms:
                action = form.get('action', '')
                if action:
                    return urljoin(base_url, action)
            # If form has no action, return contact page
            return urljoin(base_url, '/contact')
        
        return None
    
    def _extract_whatsapp(self, soup: BeautifulSoup, html: str) -> Optional[str]:
        """Extract WhatsApp link"""
        # Check for WhatsApp links
        whatsapp_pattern = r'https?://(?:wa\.me|api\.whatsapp\.com)/[\d\+\-]+'
        matches = re.findall(whatsapp_pattern, html)
        if matches:
            return matches[0]
        
        # Check links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'whatsapp' in href.lower() or 'wa.me' in href.lower():
                return href
        
        return None

