import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
from urllib.parse import urlencode, quote
from datetime import datetime
import logging

class ZillowScraper:
    def __init__(self):
        self.base_url = "https://www.zillow.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def scrape_listings(self, location, max_pages=5):
        """Scrape rental listings from Zillow for a given location"""
        listings = []
        
        try:
            # Build search URL for rentals
            search_params = {
                'searchQueryState': json.dumps({
                    'pagination': {},
                    'usersSearchTerm': location,
                    'mapBounds': {},
                    'regionSelection': [{'regionId': '', 'regionType': ''}],
                    'isMapVisible': True,
                    'filterState': {
                        'isForSaleByAgent': {'value': False},
                        'isForSaleByOwner': {'value': False},
                        'isNewConstruction': {'value': False},
                        'isForSaleForeclosure': {'value': False},
                        'isComingSoon': {'value': False},
                        'isAuction': {'value': False},
                        'isPreMarketForeclosure': {'value': False},
                        'isPreMarketPreForeclosure': {'value': False},
                        'isForRent': {'value': True}
                    },
                    'isListVisible': True
                })
            }
            
            # Alternative approach using direct rental search
            rental_url = f"{self.base_url}/homes/for_rent/{quote(location)}_rb/"
            
            self.logger.info(f"Scraping Zillow rentals for: {location}")
            
            for page in range(1, max_pages + 1):
                try:
                    # Add pagination
                    page_url = rental_url
                    if page > 1:
                        page_url += f"{page}_p/"
                    
                    response = self.session.get(page_url)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try to find property listings using multiple selectors
                        property_cards = soup.find_all('article', class_=re.compile('PropertyCard'))
                        
                        if not property_cards:
                            # Alternative selectors
                            property_cards = soup.find_all('div', class_=re.compile('property-card'))
                            
                        if not property_cards:
                            # Try to extract from script tags containing property data
                            scripts = soup.find_all('script', type='application/json')
                            for script in scripts:
                                try:
                                    data = json.loads(script.string)
                                    if 'props' in data and 'pageProps' in data['props']:
                                        search_results = data['props']['pageProps'].get('searchPageState', {})
                                        if 'cat1' in search_results and 'searchResults' in search_results['cat1']:
                                            map_results = search_results['cat1']['searchResults'].get('mapResults', [])
                                            for prop in map_results:
                                                listing = self._extract_listing_from_data(prop)
                                                if listing:
                                                    listings.append(listing)
                                except:
                                    continue
                        
                        # Parse property cards if found
                        for card in property_cards:
                            listing = self._parse_property_card(card)
                            if listing:
                                listings.append(listing)
                        
                        self.logger.info(f"Found {len(property_cards)} listings on page {page}")
                        
                        # Rate limiting
                        time.sleep(random.uniform(2, 4))
                        
                    else:
                        self.logger.warning(f"Failed to fetch page {page}: {response.status_code}")
                        
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
            
            self.logger.info(f"Scraped {len(unique_listings)} unique Zillow listings for {location}")
            return unique_listings
            
        except Exception as e:
            self.logger.error(f"Error scraping Zillow for {location}: {e}")
            return []

    def _parse_property_card(self, card):
        """Parse individual property card"""
        try:
            listing = {
                'source': 'Zillow',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract address
            address_elem = card.find('address') or card.find('span', class_=re.compile('address'))
            if address_elem:
                listing['address'] = address_elem.get_text(strip=True)
            
            # Extract price
            price_elem = card.find('span', class_=re.compile('price')) or card.find('div', class_=re.compile('price'))
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'\$([0-9,]+)', price_text)
                if price_match:
                    listing['price'] = int(price_match.group(1).replace(',', ''))
            
            # Extract bedrooms/bathrooms
            beds_elem = card.find('span', string=re.compile(r'\d+\s*bd')) or card.find('span', string=re.compile(r'\d+\s*bed'))
            if beds_elem:
                beds_match = re.search(r'(\d+)', beds_elem.get_text())
                if beds_match:
                    listing['bedrooms'] = int(beds_match.group(1))
            
            baths_elem = card.find('span', string=re.compile(r'\d+\s*ba')) or card.find('span', string=re.compile(r'\d+\s*bath'))
            if baths_elem:
                baths_match = re.search(r'(\d+)', baths_elem.get_text())
                if baths_match:
                    listing['bathrooms'] = float(baths_match.group(1))
            
            # Extract square footage
            sqft_elem = card.find('span', string=re.compile(r'\d+\s*sqft'))
            if sqft_elem:
                sqft_match = re.search(r'(\d+)', sqft_elem.get_text())
                if sqft_match:
                    listing['square_feet'] = int(sqft_match.group(1))
            
            # Extract property link
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('/'):
                    listing['url'] = self.base_url + href
                else:
                    listing['url'] = href
            
            # Extract images
            img_elem = card.find('img', src=True)
            if img_elem:
                listing['image_url'] = img_elem['src']
            
            return listing if listing.get('address') and listing.get('price') else None
            
        except Exception as e:
            self.logger.error(f"Error parsing property card: {e}")
            return None

    def _extract_listing_from_data(self, prop_data):
        """Extract listing from JSON data"""
        try:
            listing = {
                'source': 'Zillow',
                'scraped_at': datetime.now().isoformat()
            }
            
            if 'address' in prop_data:
                listing['address'] = prop_data['address']
            
            if 'price' in prop_data:
                listing['price'] = prop_data['price']
            
            if 'beds' in prop_data:
                listing['bedrooms'] = prop_data['beds']
            
            if 'baths' in prop_data:
                listing['bathrooms'] = prop_data['baths']
            
            if 'area' in prop_data:
                listing['square_feet'] = prop_data['area']
            
            if 'detailUrl' in prop_data:
                listing['url'] = self.base_url + prop_data['detailUrl']
            
            if 'imgSrc' in prop_data:
                listing['image_url'] = prop_data['imgSrc']
            
            return listing if listing.get('address') and listing.get('price') else None
            
        except Exception as e:
            self.logger.error(f"Error extracting from data: {e}")
            return None