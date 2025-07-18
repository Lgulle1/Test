#!/usr/bin/env python3
"""
Test script for Rental Listings Platform
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from app import app
from database.db_manager import DatabaseManager
from scrapers.zillow_scraper import ZillowScraper
from scrapers.apartments_scraper import ApartmentsScraper

class TestRentalPlatform(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Test database
        self.test_db = DatabaseManager("test_listings.db")
        self.test_db.init_database()
    
    def tearDown(self):
        """Clean up after tests"""
        import os
        if os.path.exists("test_listings.db"):
            os.remove("test_listings.db")
    
    def test_homepage_loads(self):
        """Test that the homepage loads successfully"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Rental Listings Platform', response.data)
    
    def test_api_listings_endpoint(self):
        """Test the API listings endpoint"""
        response = self.app.get('/api/listings')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('listings', data)
        self.assertIn('count', data)
    
    def test_api_stats_endpoint(self):
        """Test the API stats endpoint"""
        response = self.app.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('stats', data)
    
    def test_search_endpoint(self):
        """Test the search endpoint"""
        search_data = {
            'location': 'New York',
            'min_price': 1000,
            'max_price': 3000,
            'bedrooms': '2'
        }
        
        response = self.app.post('/api/search',
                               data=json.dumps(search_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_scrape_endpoint_with_location(self):
        """Test the scrape endpoint with a location"""
        scrape_data = {'location': 'San Francisco, CA'}
        
        response = self.app.post('/api/scrape',
                               data=json.dumps(scrape_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_scrape_endpoint_without_location(self):
        """Test the scrape endpoint without a location"""
        response = self.app.post('/api/scrape',
                               data=json.dumps({}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_database_operations(self):
        """Test database operations"""
        # Test saving listings
        test_listings = [
            {
                'source': 'Test',
                'address': '123 Test St, Test City',
                'price': 2000,
                'bedrooms': 2,
                'bathrooms': 1.5,
                'scraped_at': '2024-01-01T00:00:00'
            }
        ]
        
        self.test_db.save_listings(test_listings)
        
        # Test retrieving listings
        listings = self.test_db.get_all_listings()
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0]['address'], '123 Test St, Test City')
        
        # Test search
        search_results = self.test_db.search_listings('Test City', 1500, 2500, '2')
        self.assertEqual(len(search_results), 1)
        
        # Test stats
        stats = self.test_db.get_stats()
        self.assertEqual(stats['total_listings'], 1)
    
    @patch('requests.Session.get')
    def test_zillow_scraper(self, mock_get):
        """Test Zillow scraper with mocked response"""
        # Mock HTML response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'''
        <html>
            <article class="PropertyCard">
                <address>123 Main St, New York, NY</address>
                <span class="price">$2,500</span>
                <span>2 bd</span>
                <span>1 ba</span>
                <span>1000 sqft</span>
                <a href="/property/123">View Details</a>
            </article>
        </html>
        '''
        mock_get.return_value = mock_response
        
        scraper = ZillowScraper()
        listings = scraper.scrape_listings("New York, NY", max_pages=1)
        
        # Should have attempted to scrape
        mock_get.assert_called()
    
    @patch('requests.Session.get')
    def test_apartments_scraper(self, mock_get):
        """Test Apartments.com scraper with mocked response"""
        # Mock HTML response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'''
        <html>
            <article class="placard">
                <h3>Test Apartment</h3>
                <div class="property-address">456 Oak Ave, Los Angeles, CA</div>
                <p class="property-pricing">$3,000</p>
                <p class="property-beds">3 bed, 2 bath, 1200 sqft</p>
                <a href="/property/456">View Details</a>
            </article>
        </html>
        '''
        mock_get.return_value = mock_response
        
        scraper = ApartmentsScraper()
        listings = scraper.scrape_listings("Los Angeles, CA", max_pages=1)
        
        # Should have attempted to scrape
        mock_get.assert_called()

def run_tests():
    """Run all tests"""
    print("🧪 Running Rental Platform Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRentalPlatform)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print results
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)