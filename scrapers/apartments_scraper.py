import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
from urllib.parse import urlencode, quote
from datetime import datetime
import logging

class ApartmentsScraper:
    def __init__(self):
        self.base_url = "https://www.apartments.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.apartments.com'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def scrape_listings(self, location, max_pages=5):
        """Scrape rental listings from Apartments.com for a given location"""
        listings = []
        
        try:
            # Build search URL
            search_url = f"{self.base_url}/{quote(location.lower().replace(' ', '-').replace(',', ''))}"
            
            self.logger.info(f"Scraping Apartments.com for: {location}")
            
            for page in range(1, max_pages + 1):
                try:
                    # Add pagination
                    page_url = search_url
                    if page > 1:
                        page_url += f"/{page}"
                    
                    response = self.session.get(page_url)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Find property listings using multiple selectors
                        property_cards = soup.find_all('article', class_=re.compile('placard'))
                        
                        if not property_cards:
                            # Alternative selectors
                            property_cards = soup.find_all('div', class_=re.compile('property-information'))
                            
                        if not property_cards:
                            # Another alternative
                            property_cards = soup.find_all('li', class_=re.compile('mortar-wrapper'))
                        
                        # Parse property cards
                        for card in property_cards:
                            listing = self._parse_property_card(card)
                            if listing:
                                listings.append(listing)
                        
                        self.logger.info(f"Found {len(property_cards)} listings on page {page}")
                        
                        # Check if there are more pages
                        next_page = soup.find('a', {'aria-label': 'Next page'})
                        if not next_page:
                            break
                        
                        # Rate limiting
                        time.sleep(random.uniform(2, 4))
                        
                    else:
                        self.logger.warning(f"Failed to fetch page {page}: {response.status_code}")
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error scraping page {page}: {e}")
                    continue
            
            # Remove duplicates based on address
            unique_listings = []
            seen_addresses = set()
            
            for listing in listings:
                addr = listing.get('address', '').lower()
                if addr and addr not in seen_addresses:
                    seen_addresses.add(addr)
                    unique_listings.append(listing)
            
            self.logger.info(f"Scraped {len(unique_listings)} unique Apartments.com listings for {location}")
            return unique_listings
            
        except Exception as e:
            self.logger.error(f"Error scraping Apartments.com for {location}: {e}")
            return []

    def _parse_property_card(self, card):
        """Parse individual property card"""
        try:
            listing = {
                'source': 'Apartments.com',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract property name and address
            title_elem = card.find('h3') or card.find('a', class_=re.compile('property-link'))
            if title_elem:
                listing['title'] = title_elem.get_text(strip=True)
            
            # Extract address
            address_elem = card.find('div', class_=re.compile('property-address')) or card.find('p', class_=re.compile('property-address'))
            if not address_elem:
                address_elem = card.find('span', class_=re.compile('address'))
            
            if address_elem:
                listing['address'] = address_elem.get_text(strip=True)
            
            # Extract price range
            price_elem = card.find('p', class_=re.compile('property-pricing')) or card.find('span', class_=re.compile('rent'))
            if not price_elem:
                price_elem = card.find('div', class_=re.compile('price-range'))
            
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # Look for price patterns like $1,200 - $1,500 or $1,200+
                price_matches = re.findall(r'\$([0-9,]+)', price_text)
                if price_matches:
                    # Take the first price if multiple found
                    listing['price'] = int(price_matches[0].replace(',', ''))
                    if len(price_matches) > 1:
                        listing['price_max'] = int(price_matches[1].replace(',', ''))
            
            # Extract bedrooms and bathrooms
            beds_baths_elem = card.find('p', class_=re.compile('property-beds')) or card.find('span', class_=re.compile('bed-bath'))
            if not beds_baths_elem:
                beds_baths_elem = card.find('div', class_=re.compile('bed-bath-sqft'))
            
            if beds_baths_elem:
                text = beds_baths_elem.get_text(strip=True)
                
                # Extract bedrooms
                bed_match = re.search(r'(\d+)\s*(?:bed|bd|bedroom)', text, re.IGNORECASE)
                if bed_match:
                    listing['bedrooms'] = int(bed_match.group(1))
                elif 'studio' in text.lower():
                    listing['bedrooms'] = 0
                
                # Extract bathrooms
                bath_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:bath|ba|bathroom)', text, re.IGNORECASE)
                if bath_match:
                    listing['bathrooms'] = float(bath_match.group(1))
                
                # Extract square footage
                sqft_match = re.search(r'(\d+(?:,\d+)?)\s*(?:sq\.?\s*ft|sqft)', text, re.IGNORECASE)
                if sqft_match:
                    listing['square_feet'] = int(sqft_match.group(1).replace(',', ''))
            
            # Extract property link
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    listing['url'] = self.base_url + href
                elif href.startswith('http'):
                    listing['url'] = href
                else:
                    listing['url'] = self.base_url + '/' + href
            
            # Extract image
            img_elem = card.find('img', src=True)
            if img_elem:
                src = img_elem['src']
                if src.startswith('//'):
                    listing['image_url'] = 'https:' + src
                elif src.startswith('/'):
                    listing['image_url'] = self.base_url + src
                else:
                    listing['image_url'] = src
            
            # Extract amenities if available
            amenities_elem = card.find('div', class_=re.compile('amenity')) or card.find('ul', class_=re.compile('amenity'))
            if amenities_elem:
                amenities = []
                for amenity in amenities_elem.find_all('li') or amenities_elem.find_all('span'):
                    amenities.append(amenity.get_text(strip=True))
                if amenities:
                    listing['amenities'] = amenities
            
            # Extract phone number if available
            phone_elem = card.find('a', href=re.compile(r'tel:'))
            if phone_elem:
                listing['phone'] = phone_elem.get_text(strip=True)
            
            return listing if listing.get('address') and listing.get('price') else None
            
        except Exception as e:
            self.logger.error(f"Error parsing property card: {e}")
            return None

    def get_property_details(self, property_url):
        """Get detailed information for a specific property"""
        try:
            response = self.session.get(property_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                details = {}
                
                # Extract detailed amenities
                amenities_section = soup.find('div', class_=re.compile('amenities'))
                if amenities_section:
                    amenities = []
                    for amenity in amenities_section.find_all('li'):
                        amenities.append(amenity.get_text(strip=True))
                    details['amenities'] = amenities
                
                # Extract property description
                description_elem = soup.find('div', class_=re.compile('description')) or soup.find('p', class_=re.compile('description'))
                if description_elem:
                    details['description'] = description_elem.get_text(strip=True)
                
                # Extract contact information
                contact_elem = soup.find('div', class_=re.compile('contact'))
                if contact_elem:
                    phone_elem = contact_elem.find('a', href=re.compile(r'tel:'))
                    if phone_elem:
                        details['phone'] = phone_elem.get_text(strip=True)
                
                # Extract more images
                image_gallery = soup.find('div', class_=re.compile('photo-gallery'))
                if image_gallery:
                    images = []
                    for img in image_gallery.find_all('img', src=True):
                        src = img['src']
                        if src.startswith('//'):
                            images.append('https:' + src)
                        elif src.startswith('/'):
                            images.append(self.base_url + src)
                        else:
                            images.append(src)
                    details['images'] = images
                
                return details
                
        except Exception as e:
            self.logger.error(f"Error getting property details: {e}")
            return {}