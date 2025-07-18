// Main JavaScript for Rental Listings Platform

class RentalPlatform {
    constructor() {
        this.listings = [];
        this.currentSearch = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
    }

    bindEvents() {
        // Search form
        document.getElementById('search-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });

        // Scrape button
        document.getElementById('scrape-btn').addEventListener('click', () => {
            this.triggerScraping();
        });

        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadListings();
        });
    }

    async loadInitialData() {
        await Promise.all([
            this.loadListings(),
            this.loadStats()
        ]);
    }

    async loadListings() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/listings');
            const data = await response.json();
            
            if (data.success) {
                this.listings = data.listings;
                this.displayListings(this.listings);
                this.updateListingCount(this.listings.length);
            } else {
                this.showToast('Error loading listings: ' + data.error, 'error');
            }
        } catch (error) {
            this.showToast('Error loading listings: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (data.success) {
                this.displayStats(data.stats);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async performSearch() {
        const location = document.getElementById('location').value;
        const bedrooms = document.getElementById('bedrooms').value;
        const minPrice = parseInt(document.getElementById('min-price').value) || 0;
        const maxPrice = parseInt(document.getElementById('max-price').value) || 10000;

        this.currentSearch = { location, bedrooms, min_price: minPrice, max_price: maxPrice };

        try {
            this.showLoading();
            
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.currentSearch)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.listings = data.listings;
                this.displayListings(this.listings);
                this.updateListingCount(this.listings.length);
                
                if (this.listings.length === 0) {
                    this.showNoResults();
                }
            } else {
                this.showToast('Search error: ' + data.error, 'error');
            }
        } catch (error) {
            this.showToast('Search error: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async triggerScraping() {
        const location = document.getElementById('location').value;
        
        if (!location) {
            this.showToast('Please enter a location to scrape', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ location })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast(data.message, 'success');
                
                // Refresh listings after a delay
                setTimeout(() => {
                    this.loadListings();
                    this.loadStats();
                }, 5000);
            } else {
                this.showToast('Scraping error: ' + data.error, 'error');
            }
        } catch (error) {
            this.showToast('Scraping error: ' + error.message, 'error');
        }
    }

    displayListings(listings) {
        const container = document.getElementById('listings-container');
        
        if (listings.length === 0) {
            this.showNoResults();
            return;
        }

        container.innerHTML = listings.map(listing => this.createListingCard(listing)).join('');
        
        // Add fade-in animation
        container.querySelectorAll('.card').forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('fade-in');
            }, index * 100);
        });
        
        this.hideNoResults();
    }

    createListingCard(listing) {
        const price = listing.price ? `$${listing.price.toLocaleString()}` : 'Price N/A';
        const priceMax = listing.price_max ? ` - $${listing.price_max.toLocaleString()}` : '';
        const bedrooms = listing.bedrooms !== null ? `${listing.bedrooms} bed` : '';
        const bathrooms = listing.bathrooms !== null ? `${listing.bathrooms} bath` : '';
        const sqft = listing.square_feet ? `${listing.square_feet.toLocaleString()} sqft` : '';
        
        const sourceClass = listing.source === 'Zillow' ? 'source-zillow' : 'source-apartments';
        
        const imageHtml = listing.image_url 
            ? `<img src="${listing.image_url}" class="listing-image" alt="Property image">`
            : `<div class="no-image-placeholder"><i class="fas fa-home"></i></div>`;
        
        const amenitiesHtml = listing.amenities && listing.amenities.length > 0
            ? listing.amenities.slice(0, 3).map(amenity => 
                `<span class="amenity-tag">${amenity}</span>`
              ).join('')
            : '';

        return `
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card listing-card shadow-sm">
                    ${imageHtml}
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div class="listing-price">${price}${priceMax}</div>
                            <span class="listing-source ${sourceClass}">${listing.source}</span>
                        </div>
                        
                        <div class="listing-address">${listing.address || 'Address not available'}</div>
                        
                        <div class="listing-specs">
                            ${bedrooms ? `<div class="spec-item"><i class="fas fa-bed"></i> ${bedrooms}</div>` : ''}
                            ${bathrooms ? `<div class="spec-item"><i class="fas fa-bath"></i> ${bathrooms}</div>` : ''}
                            ${sqft ? `<div class="spec-item"><i class="fas fa-ruler-combined"></i> ${sqft}</div>` : ''}
                        </div>
                        
                        ${amenitiesHtml ? `<div class="mb-2">${amenitiesHtml}</div>` : ''}
                        
                        ${listing.url ? `
                            <a href="${listing.url}" target="_blank" class="btn btn-primary btn-sm">
                                <i class="fas fa-external-link-alt me-1"></i>
                                View Details
                            </a>
                        ` : ''}
                        
                        ${listing.phone ? `
                            <a href="tel:${listing.phone}" class="btn btn-outline-secondary btn-sm ms-2">
                                <i class="fas fa-phone me-1"></i>
                                Call
                            </a>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    displayStats(stats) {
        const container = document.getElementById('stats-cards');
        
        const statsCards = [
            {
                title: 'Total Listings',
                value: stats.total_listings || 0,
                icon: 'fas fa-home',
                color: 'primary'
            },
            {
                title: 'Average Price',
                value: stats.average_price ? `$${stats.average_price.toLocaleString()}` : '$0',
                icon: 'fas fa-dollar-sign',
                color: 'success'
            },
            {
                title: 'Recent Listings',
                value: stats.recent_listings || 0,
                icon: 'fas fa-clock',
                color: 'info'
            },
            {
                title: 'Sources',
                value: Object.keys(stats.by_source || {}).length,
                icon: 'fas fa-database',
                color: 'warning'
            }
        ];

        container.innerHTML = statsCards.map(stat => `
            <div class="col-lg-3 col-md-6 mb-3">
                <div class="stat-card">
                    <div class="d-flex align-items-center">
                        <div class="me-3">
                            <i class="${stat.icon} fa-2x"></i>
                        </div>
                        <div>
                            <h4>${stat.value}</h4>
                            <p>${stat.title}</p>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateListingCount(count) {
        document.getElementById('listing-count').textContent = `${count} listing${count !== 1 ? 's' : ''} found`;
    }

    showLoading() {
        document.getElementById('loading-spinner').classList.remove('d-none');
        document.getElementById('listings-container').style.opacity = '0.5';
    }

    hideLoading() {
        document.getElementById('loading-spinner').classList.add('d-none');
        document.getElementById('listings-container').style.opacity = '1';
    }

    showNoResults() {
        document.getElementById('no-results').classList.remove('d-none');
    }

    hideNoResults() {
        document.getElementById('no-results').classList.add('d-none');
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('notification-toast');
        const toastBody = document.getElementById('toast-message');
        const toastHeader = toast.querySelector('.toast-header');
        
        // Update message
        toastBody.textContent = message;
        
        // Update icon and color based on type
        const icon = toastHeader.querySelector('i');
        icon.className = 'me-2';
        
        switch (type) {
            case 'success':
                icon.classList.add('fas', 'fa-check-circle', 'text-success');
                break;
            case 'error':
                icon.classList.add('fas', 'fa-exclamation-circle', 'text-danger');
                break;
            case 'warning':
                icon.classList.add('fas', 'fa-exclamation-triangle', 'text-warning');
                break;
            default:
                icon.classList.add('fas', 'fa-info-circle', 'text-primary');
        }
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
}

// Initialize the platform when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RentalPlatform();
});