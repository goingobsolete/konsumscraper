from bs4 import BeautifulSoup
from datetime import datetime
import json
from urllib.parse import urljoin
from typing import Set, Optional

from .page_downloader import PageDownloader

class CategoryScraper:
    def __init__(self):
        self.base_url = 'https://www.konsum-leipzig.de'
        self.start_url = f"{self.base_url}/online-bestellen/alle-produkte/"
        self.categories = set()
        self.visited_urls = set()
        self.downloader = PageDownloader()

    def extract_breadcrumb_path(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract category path from breadcrumbs"""
        breadcrumb = soup.find('nav', class_='content--breadcrumb')
        if breadcrumb:
            links = breadcrumb.find_all('a', class_='breadcrumb--link')
            # Skip the "Online bestellen" part and get the rest of the path
            path_parts = [link.get_text(strip=True) for link in links[1:]]
            return ' > '.join(path_parts) if path_parts else None
        return None

    def scrape_categories(self, url: Optional[str] = None) -> None:
        """Recursively scrape category pages"""
        if url is None:
            url = self.start_url
            
        if url in self.visited_urls:
            return
            
        self.visited_urls.add(url)
        
        print(f"Checking: {url}")
        content = self.downloader.download_page(url)
        if not content:
            return
            
        soup = BeautifulSoup(content, 'html.parser')

        # Get current category path from breadcrumbs
        category_path = self.extract_breadcrumb_path(soup)
        if category_path:
            self.categories.add(category_path)
            print(f"Found category: {category_path}")

        # Find subcategory container
        sidebar = soup.find('div', class_='sidebar--categories-navigation')
        if sidebar:
            # Look for subcategory links
            subcategory_links = sidebar.find_all('a', class_='navigation--link')
            for link in subcategory_links:
                href = link.get('href', '')
                # Only follow links to product categories
                if '/online-bestellen/alle-produkte/' in href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in self.visited_urls:
                        self.scrape_categories(full_url)

    def save_categories(self) -> None:
        """Save scraped categories to files"""
        if not self.categories:
            print("No categories found!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save categories to config directory
        config_file = '../config/categories.json'
        categories_data = {
            "total_categories": len(self.categories),
            "categories": sorted(self.categories, key=lambda x: (len(x.split(' > ')), x)),
            "scrape_date": datetime.now().isoformat()
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(categories_data, f, indent=4, ensure_ascii=False)

        print(f"\nFound {len(self.categories)} categories")
        print(f"Saved to {config_file}")

def main():
    """Run category scraper"""
    try:
        print("Starting category scraper...")
        scraper = CategoryScraper()
        scraper.scrape_categories()
    except KeyboardInterrupt:
        print("\nScraping interrupted by user...")
    finally:
        scraper.save_categories()

if __name__ == "__main__":
    main()