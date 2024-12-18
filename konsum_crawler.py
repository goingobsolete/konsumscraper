# Import required libraries
import requests  # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML content
from urllib.parse import urljoin, urlparse  # For URL manipulation and parsing

# Define the main scraper class
class KonsumSiteScraper:
    def __init__(self, start_url='https://www.konsum-leipzig.de/online-bestellen/'):
        # Initialize class attributes
        self.base_url = 'https://www.konsum-leipzig.de'  # Base website URL
        self.start_url = start_url  # Starting point for crawling
        self.visited_urls = set()  # Keep track of URLs we've already crawled
        self.product_urls = set()  # Store found product URLs
        self.headers = {  # Browser-like headers to avoid being blocked
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def is_valid_url(self, url):
        """Check if a URL should be crawled"""
        parsed = urlparse(url)  # Parse URL into components
        return (
            parsed.netloc == 'www.konsum-leipzig.de' and  # Must be on Konsum Leipzig domain
            '/online-bestellen/' in url and  # Must be in online shop section
            not url.endswith(('.jpg', '.png', '.pdf')) and  # Exclude media files
            '/checkout/' not in url and  # Exclude checkout pages
            '/account/' not in url  # Exclude account pages
        )

    def is_product_page(self, url):
        """Determine if URL is a product page"""
        return (
            '/online-bestellen/' in url and  # Must be in online shop
            len(url.split('/')[-1].split('?')[0]) > 5  # Product pages typically have long identifiers
        )

    def crawl(self, url=None, depth=3):
        """Main crawling method"""
        if url is None:
            url = self.start_url  # Use default start URL if none provided

        # Stop conditions
        if (url in self.visited_urls or depth < 0):
            return

        # Add URL to visited set
        self.visited_urls.add(url)

        try:
            # Get page content
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # If this is a product page, add to product URLs
            if self.is_product_page(url):
                self.product_urls.add(url)
                print(f"Found product page: {url}")

            # Find and process all links on the page
            for link in soup.find_all('a', href=True):
                # Convert relative URLs to absolute
                full_url = urljoin(self.base_url, link['href'])

                # Check if URL should be crawled
                if (self.is_valid_url(full_url) and 
                    full_url not in self.visited_urls):
                    # Recursive call with decreased depth
                    self.crawl(full_url, depth - 1)

        except requests.RequestException as e:
            print(f"Error crawling {url}: {e}")

# Code to run if script is executed directly
if __name__ == "__main__":
    site_scraper = KonsumSiteScraper()  # Create scraper instance
    site_scraper.crawl()  # Start crawling
    
    # Print all found product URLs
    print("Found product pages:")
    for product_url in site_scraper.product_urls:
        print(product_url)