# Rental Listings Platform

A comprehensive web platform that scrapes rental listings from popular real estate websites including Zillow and Apartments.com. Built with Python Flask backend and modern web frontend.

## Features

### 🏠 **Multi-Source Data Collection**
- **Zillow Integration**: Scrapes rental listings from Zillow
- **Apartments.com Integration**: Extracts property data from Apartments.com
- **Intelligent Deduplication**: Removes duplicate listings based on address and price
- **Rate Limiting**: Respectful scraping with delays to avoid being blocked

### 🔍 **Advanced Search & Filtering**
- **Location-based Search**: Find rentals in specific cities or areas
- **Price Range Filtering**: Set minimum and maximum price limits
- **Bedroom Filtering**: Filter by number of bedrooms (Studio to 4+)
- **Real-time Results**: Instant search with modern AJAX interface

### 📊 **Analytics Dashboard**
- **Platform Statistics**: Total listings, average prices, recent activity
- **Source Breakdown**: Listings by data source (Zillow vs Apartments.com)
- **Price Analytics**: Min/max price ranges and distribution
- **Location Insights**: Popular cities and listing counts

### 🎨 **Modern Web Interface**
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Bootstrap 5**: Modern, clean UI with smooth animations
- **Interactive Cards**: Hover effects and detailed property information
- **Toast Notifications**: Real-time feedback for user actions

### 🔄 **Automated Data Management**
- **Scheduled Scraping**: Automatic data collection every 6 hours for popular cities
- **Database Storage**: SQLite database with optimized indexes
- **Data Cleanup**: Automatic removal of old listings (30+ days)
- **Background Processing**: Non-blocking scraping operations

## Project Structure

```
rental-listings-platform/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── scrapers/              # Web scraping modules
│   ├── __init__.py
│   ├── zillow_scraper.py  # Zillow scraping logic
│   └── apartments_scraper.py # Apartments.com scraping logic
├── database/              # Database management
│   ├── __init__.py
│   └── db_manager.py      # SQLite database operations
├── templates/             # HTML templates
│   └── index.html         # Main dashboard template
└── static/                # Static assets
    ├── css/
    │   └── style.css      # Custom styles
    └── js/
        └── main.js        # Frontend JavaScript
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd rental-listings-platform
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the platform**:
   Open your browser and go to `http://localhost:5000`

### Development Setup

For development with auto-reload:
```bash
export FLASK_ENV=development
python app.py
```

## Usage Guide

### 🔍 **Searching for Listings**

1. **Basic Search**:
   - Enter a location (e.g., "New York, NY", "Los Angeles, CA")
   - Click "Search Listings"

2. **Advanced Filtering**:
   - Set price range (min/max)
   - Select number of bedrooms
   - Combine multiple filters for precise results

3. **View Results**:
   - Browse property cards with images, prices, and details
   - Click "View Details" to visit the original listing
   - Use "Call" button to contact property directly

### 📥 **Scraping New Data**

1. **Manual Scraping**:
   - Enter a location in the search form
   - Click "Scrape New Data"
   - Wait for notification confirming scraping started
   - Refresh after a few minutes to see new results

2. **Automatic Scraping**:
   - The platform automatically scrapes popular cities every 6 hours
   - No manual intervention required
   - Check the "Recent Listings" stat to see latest activity

### 📊 **Platform Statistics**

The dashboard automatically displays:
- **Total Listings**: Current number of properties in database
- **Average Price**: Mean rental price across all listings
- **Recent Listings**: Properties added in the last 24 hours
- **Sources**: Number of data sources active

## API Endpoints

### `GET /`
Main dashboard page

### `POST /api/search`
Search for rental listings
```json
{
  "location": "New York, NY",
  "min_price": 1000,
  "max_price": 3000,
  "bedrooms": "2"
}
```

### `GET /api/listings`
Get all recent listings (limited to 100)

### `POST /api/scrape`
Trigger manual scraping for a location
```json
{
  "location": "San Francisco, CA"
}
```

### `GET /api/stats`
Get platform statistics and analytics

## Database Schema

### Listings Table
- `id`: Primary key
- `source`: Data source (Zillow, Apartments.com)
- `title`: Property title/name
- `address`: Full property address
- `price`: Rental price (minimum)
- `price_max`: Maximum price (for ranges)
- `bedrooms`: Number of bedrooms
- `bathrooms`: Number of bathrooms
- `square_feet`: Property size
- `url`: Link to original listing
- `image_url`: Property image
- `amenities`: JSON array of amenities
- `phone`: Contact phone number
- `description`: Property description
- `scraped_at`: When data was scraped
- `created_at`: Database insertion time

## Technical Features

### Web Scraping
- **Robust Selectors**: Multiple CSS selector strategies for reliable data extraction
- **Error Handling**: Graceful failure handling with logging
- **Rate Limiting**: Random delays between requests (2-4 seconds)
- **Session Management**: Persistent HTTP sessions with proper headers

### Database
- **SQLite**: Lightweight, file-based database
- **Indexes**: Optimized queries with location, price, and bedroom indexes
- **Unique Constraints**: Prevents duplicate listings
- **JSON Support**: Structured amenities data

### Frontend
- **Responsive Grid**: Bootstrap 5 card layout
- **AJAX**: Asynchronous API calls without page reloads
- **Loading States**: Visual feedback during operations
- **Error Handling**: User-friendly error messages

## Configuration

### Environment Variables
- `FLASK_ENV`: Set to 'development' for debug mode
- `DATABASE_PATH`: Custom database file location (optional)

### Customization
- **Popular Cities**: Modify the `popular_locations` list in `app.py`
- **Scraping Frequency**: Change the schedule interval (currently 6 hours)
- **Rate Limits**: Adjust delays in scraper files
- **Page Limits**: Modify `max_pages` parameter in scrapers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Legal Considerations

- **Respect robots.txt**: The scrapers respect website terms of service
- **Rate Limiting**: Implemented to avoid overwhelming target servers
- **Public Data**: Only scrapes publicly available rental listings
- **Educational Purpose**: Intended for learning and personal use

## Troubleshooting

### Common Issues

1. **No listings found**:
   - Check if the location is spelled correctly
   - Try scraping new data for that location
   - Verify internet connection

2. **Scraping fails**:
   - Websites may have changed their structure
   - Check the console for error messages
   - Try a different location

3. **Database errors**:
   - Ensure write permissions in the application directory
   - Check disk space availability

### Logs
Application logs are displayed in the console. For production, redirect to files:
```bash
python app.py > app.log 2>&1
```

## Future Enhancements

- **Additional Sources**: Integrate more rental websites
- **Email Alerts**: Notify users of new listings matching criteria
- **Price History**: Track price changes over time
- **Map Integration**: Display listings on interactive maps
- **User Accounts**: Save searches and favorites
- **Mobile App**: React Native or Flutter mobile application

## License

This project is for educational purposes. Please ensure compliance with target websites' terms of service and robots.txt files when using.

---

**Note**: This platform is designed for educational and personal use. Always respect website terms of service and implement appropriate delays when scraping data.