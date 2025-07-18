from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
from scrapers.zillow_scraper import ZillowScraper
from scrapers.apartments_scraper import ApartmentsScraper
from database.db_manager import DatabaseManager
import threading
import schedule
import time

app = Flask(__name__)
CORS(app)

# Initialize database
db = DatabaseManager()

# Initialize scrapers
zillow_scraper = ZillowScraper()
apartments_scraper = ApartmentsScraper()

@app.route('/')
def index():
    """Serve the main dashboard"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_listings():
    """Search for rental listings"""
    data = request.json
    location = data.get('location', '')
    min_price = data.get('min_price', 0)
    max_price = data.get('max_price', 10000)
    bedrooms = data.get('bedrooms', '')
    
    try:
        # Get listings from database
        listings = db.search_listings(location, min_price, max_price, bedrooms)
        return jsonify({
            'success': True,
            'listings': listings,
            'count': len(listings)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scrape', methods=['POST'])
def trigger_scrape():
    """Manually trigger scraping for a location"""
    data = request.json
    location = data.get('location', '')
    
    if not location:
        return jsonify({
            'success': False,
            'error': 'Location is required'
        }), 400
    
    try:
        # Run scraping in background
        def run_scrape():
            print(f"Starting scrape for {location}")
            
            # Scrape Zillow
            zillow_listings = zillow_scraper.scrape_listings(location)
            print(f"Found {len(zillow_listings)} Zillow listings")
            
            # Scrape Apartments.com
            apartments_listings = apartments_scraper.scrape_listings(location)
            print(f"Found {len(apartments_listings)} Apartments.com listings")
            
            # Save to database
            all_listings = zillow_listings + apartments_listings
            db.save_listings(all_listings)
            print(f"Saved {len(all_listings)} total listings to database")
        
        thread = threading.Thread(target=run_scrape)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Started scraping for {location}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/listings')
def get_all_listings():
    """Get all listings from database"""
    try:
        listings = db.get_all_listings()
        return jsonify({
            'success': True,
            'listings': listings,
            'count': len(listings)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get platform statistics"""
    try:
        stats = db.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def scheduled_scraping():
    """Run scheduled scraping for popular locations"""
    popular_locations = [
        "New York, NY",
        "Los Angeles, CA", 
        "Chicago, IL",
        "Houston, TX",
        "Phoenix, AZ"
    ]
    
    for location in popular_locations:
        try:
            print(f"Scheduled scraping for {location}")
            
            # Scrape both sources
            zillow_listings = zillow_scraper.scrape_listings(location)
            apartments_listings = apartments_scraper.scrape_listings(location)
            
            # Save to database
            all_listings = zillow_listings + apartments_listings
            db.save_listings(all_listings)
            
            print(f"Completed scheduled scraping for {location}: {len(all_listings)} listings")
            
            # Wait between locations to be respectful
            time.sleep(30)
            
        except Exception as e:
            print(f"Error in scheduled scraping for {location}: {e}")

def run_scheduler():
    """Run the scheduler in a separate thread"""
    schedule.every(6).hours.do(scheduled_scraping)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    # Initialize database tables
    db.init_database()
    
    # Start scheduler in background
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)