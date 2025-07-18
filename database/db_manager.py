import sqlite3
import json
from datetime import datetime
import logging
import os

class DatabaseManager:
    def __init__(self, db_path="rental_listings.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create listings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    title TEXT,
                    address TEXT NOT NULL,
                    price INTEGER,
                    price_max INTEGER,
                    bedrooms INTEGER,
                    bathrooms REAL,
                    square_feet INTEGER,
                    url TEXT,
                    image_url TEXT,
                    amenities TEXT,
                    phone TEXT,
                    description TEXT,
                    scraped_at TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source, address, price) ON CONFLICT REPLACE
                )
            ''')
            
            # Create search index
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_location 
                ON listings(address)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_price 
                ON listings(price)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_bedrooms 
                ON listings(bedrooms)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_source 
                ON listings(source)
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            
    def save_listings(self, listings):
        """Save a list of listings to the database"""
        if not listings:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            saved_count = 0
            
            for listing in listings:
                try:
                    # Convert amenities list to JSON string
                    amenities_json = None
                    if 'amenities' in listing and listing['amenities']:
                        amenities_json = json.dumps(listing['amenities'])
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO listings 
                        (source, title, address, price, price_max, bedrooms, 
                         bathrooms, square_feet, url, image_url, amenities, 
                         phone, description, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        listing.get('source'),
                        listing.get('title'),
                        listing.get('address'),
                        listing.get('price'),
                        listing.get('price_max'),
                        listing.get('bedrooms'),
                        listing.get('bathrooms'),
                        listing.get('square_feet'),
                        listing.get('url'),
                        listing.get('image_url'),
                        amenities_json,
                        listing.get('phone'),
                        listing.get('description'),
                        listing.get('scraped_at')
                    ))
                    
                    saved_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Error saving listing: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Saved {saved_count} listings to database")
            
        except Exception as e:
            self.logger.error(f"Error saving listings to database: {e}")
    
    def search_listings(self, location="", min_price=0, max_price=10000, bedrooms=""):
        """Search for listings based on criteria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT * FROM listings WHERE 1=1"
            params = []
            
            if location:
                query += " AND address LIKE ?"
                params.append(f"%{location}%")
            
            if min_price > 0:
                query += " AND price >= ?"
                params.append(min_price)
            
            if max_price < 10000:
                query += " AND price <= ?"
                params.append(max_price)
            
            if bedrooms and bedrooms.isdigit():
                query += " AND bedrooms = ?"
                params.append(int(bedrooms))
            
            query += " ORDER BY created_at DESC LIMIT 100"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = [description[0] for description in cursor.description]
            listings = []
            
            for row in rows:
                listing = dict(zip(columns, row))
                
                # Parse amenities JSON
                if listing['amenities']:
                    try:
                        listing['amenities'] = json.loads(listing['amenities'])
                    except:
                        listing['amenities'] = []
                
                listings.append(listing)
            
            conn.close()
            return listings
            
        except Exception as e:
            self.logger.error(f"Error searching listings: {e}")
            return []
    
    def get_all_listings(self, limit=100):
        """Get all listings from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM listings ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = [description[0] for description in cursor.description]
            listings = []
            
            for row in rows:
                listing = dict(zip(columns, row))
                
                # Parse amenities JSON
                if listing['amenities']:
                    try:
                        listing['amenities'] = json.loads(listing['amenities'])
                    except:
                        listing['amenities'] = []
                
                listings.append(listing)
            
            conn.close()
            return listings
            
        except Exception as e:
            self.logger.error(f"Error getting all listings: {e}")
            return []
    
    def get_stats(self):
        """Get platform statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Total listings
            cursor.execute("SELECT COUNT(*) FROM listings")
            stats['total_listings'] = cursor.fetchone()[0]
            
            # Listings by source
            cursor.execute("SELECT source, COUNT(*) FROM listings GROUP BY source")
            source_counts = cursor.fetchall()
            stats['by_source'] = {source: count for source, count in source_counts}
            
            # Average price
            cursor.execute("SELECT AVG(price) FROM listings WHERE price > 0")
            avg_price = cursor.fetchone()[0]
            stats['average_price'] = round(avg_price, 2) if avg_price else 0
            
            # Price range
            cursor.execute("SELECT MIN(price), MAX(price) FROM listings WHERE price > 0")
            price_range = cursor.fetchone()
            stats['price_range'] = {
                'min': price_range[0] if price_range[0] else 0,
                'max': price_range[1] if price_range[1] else 0
            }
            
            # Bedroom distribution
            cursor.execute("SELECT bedrooms, COUNT(*) FROM listings WHERE bedrooms IS NOT NULL GROUP BY bedrooms ORDER BY bedrooms")
            bedroom_dist = cursor.fetchall()
            stats['bedroom_distribution'] = {str(beds): count for beds, count in bedroom_dist}
            
            # Recent activity (last 24 hours)
            cursor.execute("SELECT COUNT(*) FROM listings WHERE created_at > datetime('now', '-1 day')")
            stats['recent_listings'] = cursor.fetchone()[0]
            
            # Top locations
            cursor.execute("""
                SELECT SUBSTR(address, 1, INSTR(address, ',') - 1) as city, COUNT(*) as count 
                FROM listings 
                WHERE address LIKE '%,%' 
                GROUP BY city 
                ORDER BY count DESC 
                LIMIT 10
            """)
            top_locations = cursor.fetchall()
            stats['top_locations'] = {city: count for city, count in top_locations if city}
            
            conn.close()
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {}
    
    def clean_old_listings(self, days=30):
        """Remove listings older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM listings WHERE created_at < datetime('now', '-' || ? || ' days')", (days,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cleaned {deleted_count} old listings")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning old listings: {e}")
            return 0