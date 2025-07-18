import random
from datetime import datetime
from faker import Faker

class DemoDataGenerator:
    def __init__(self):
        self.fake = Faker()
        
        # Sample data for realistic listings
        self.cities = [
            "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX",
            "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX", "San Diego, CA",
            "Dallas, TX", "San Jose, CA", "Austin, TX", "Jacksonville, FL",
            "Fort Worth, TX", "Columbus, OH", "Charlotte, NC", "San Francisco, CA",
            "Indianapolis, IN", "Seattle, WA", "Denver, CO", "Washington, DC"
        ]
        
        self.amenities = [
            "Pool", "Gym", "Parking", "Pet Friendly", "Air Conditioning",
            "Laundry", "Dishwasher", "Balcony", "Hardwood Floors", "Walk-in Closet",
            "In-unit Washer/Dryer", "Stainless Steel Appliances", "Granite Countertops",
            "Central Air", "Fireplace", "Garden", "Rooftop Deck", "Concierge",
            "Elevator", "Storage", "Bike Storage", "WiFi", "Cable Ready"
        ]
        
        self.property_types = [
            "Modern Apartment", "Luxury Condo", "Studio Loft", "Garden Apartment",
            "High-rise", "Townhouse", "Duplex", "Penthouse", "Converted Loft",
            "Ranch Style", "Victorian", "Contemporary", "Traditional"
        ]

    def generate_listings(self, count=50):
        """Generate demo rental listings"""
        listings = []
        
        for _ in range(count):
            city = random.choice(self.cities)
            bedrooms = random.choice([0, 1, 1, 2, 2, 2, 3, 3, 4])
            bathrooms = random.choice([1, 1.5, 2, 2.5, 3])
            
            # Generate realistic pricing based on city and size
            base_prices = {
                "New York, NY": 3500, "San Francisco, CA": 3200, "Los Angeles, CA": 2800,
                "Seattle, WA": 2400, "Washington, DC": 2300, "Boston, MA": 2200,
                "Chicago, IL": 1800, "Austin, TX": 1600, "Denver, CO": 1700,
                "Dallas, TX": 1400, "Houston, TX": 1300, "Phoenix, AZ": 1200
            }
            
            base_price = base_prices.get(city, 1500)
            bedroom_multiplier = max(1, bedrooms) * 0.8 + 0.2
            price = int(base_price * bedroom_multiplier * random.uniform(0.7, 1.3))
            
            # Generate square footage
            sq_ft = random.randint(400, 2500)
            if bedrooms == 0:  # Studio
                sq_ft = random.randint(300, 700)
            elif bedrooms == 1:
                sq_ft = random.randint(500, 900)
            elif bedrooms == 2:
                sq_ft = random.randint(800, 1400)
            elif bedrooms >= 3:
                sq_ft = random.randint(1200, 2500)
            
            # Select random amenities
            selected_amenities = random.sample(self.amenities, random.randint(3, 8))
            
            # Generate address
            street_address = f"{random.randint(100, 9999)} {self.fake.street_name()}"
            
            listing = {
                'source': random.choice(['Zillow', 'Apartments.com']),
                'title': f"{random.choice(self.property_types)} - {bedrooms if bedrooms > 0 else 'Studio'} Bed",
                'address': f"{street_address}, {city}",
                'price': price,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'square_feet': sq_ft,
                'url': f"https://{'zillow.com' if random.choice([True, False]) else 'apartments.com'}/listing/{random.randint(100000, 999999)}",
                'image_url': f"https://images.unsplash.com/photo-{random.randint(1500000000, 1600000000)}-{self.fake.uuid4()[:8]}?w=400&h=300&fit=crop&auto=format",
                'amenities': selected_amenities,
                'phone': self.fake.phone_number(),
                'description': f"Beautiful {bedrooms if bedrooms > 0 else 'studio'} bedroom apartment in {city.split(',')[0]}. {self.fake.text(max_nb_chars=200)}",
                'scraped_at': datetime.now().isoformat()
            }
            
            listings.append(listing)
        
        return listings

    def generate_for_location(self, location, count=20):
        """Generate demo listings for a specific location"""
        listings = []
        
        for _ in range(count):
            bedrooms = random.choice([0, 1, 1, 2, 2, 2, 3, 3, 4])
            bathrooms = random.choice([1, 1.5, 2, 2.5, 3])
            
            # Generate pricing based on location
            if any(expensive_city in location.lower() for expensive_city in ['new york', 'san francisco', 'manhattan']):
                base_price = random.randint(2500, 5000)
            elif any(moderate_city in location.lower() for moderate_city in ['los angeles', 'chicago', 'seattle']):
                base_price = random.randint(1800, 3500)
            else:
                base_price = random.randint(1000, 2500)
            
            bedroom_multiplier = max(1, bedrooms) * 0.8 + 0.2
            price = int(base_price * bedroom_multiplier * random.uniform(0.8, 1.2))
            
            # Generate square footage
            sq_ft = random.randint(400, 2500)
            if bedrooms == 0:  # Studio
                sq_ft = random.randint(300, 700)
            elif bedrooms == 1:
                sq_ft = random.randint(500, 900)
            elif bedrooms == 2:
                sq_ft = random.randint(800, 1400)
            elif bedrooms >= 3:
                sq_ft = random.randint(1200, 2500)
            
            # Select random amenities
            selected_amenities = random.sample(self.amenities, random.randint(3, 8))
            
            # Generate address for the specific location
            street_address = f"{random.randint(100, 9999)} {self.fake.street_name()}"
            
            listing = {
                'source': random.choice(['Zillow', 'Apartments.com']),
                'title': f"{random.choice(self.property_types)} - {bedrooms if bedrooms > 0 else 'Studio'} Bed",
                'address': f"{street_address}, {location}",
                'price': price,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'square_feet': sq_ft,
                'url': f"https://{'zillow.com' if random.choice([True, False]) else 'apartments.com'}/listing/{random.randint(100000, 999999)}",
                'image_url': f"https://images.unsplash.com/photo-{random.randint(1500000000, 1600000000)}-{self.fake.uuid4()[:8]}?w=400&h=300&fit=crop&auto=format",
                'amenities': selected_amenities,
                'phone': self.fake.phone_number(),
                'description': f"Beautiful {bedrooms if bedrooms > 0 else 'studio'} bedroom apartment in {location}. {self.fake.text(max_nb_chars=200)}",
                'scraped_at': datetime.now().isoformat()
            }
            
            listings.append(listing)
        
        return listings