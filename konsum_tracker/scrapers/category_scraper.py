from bs4 import BeautifulSoup
from datetime import datetime
import json
from urllib.parse import urljoin
from typing import Set, Optional
from pathlib import Path

from .page_downloader import PageDownloader

class CategoryScraper:
    def __init__(self):
        print("Initializing CategoryScraper...")  # Debug print
        self.base_url = 'https://www.konsum-leipzig.de'
        self.start_url = f"{self.base_url}/online-bestellen/alle-produkte/"
        self.categories = set()
        self.visited_urls = set()
        self.downloader = PageDownloader()
        self.config_dir = Path(__file__).parent.parent / 'config'
        print(f"Config directory set to: {self.config_dir}")  # Debug print

    def extract_breadcrumb_path(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract category path from breadcrumbs"""
        breadcrumb = soup.find('nav', class_='content--breadcrumb')
        if breadcrumb:
            links = breadcrumb.find_all('a', class_='breadcrumb--link')
            path_parts = [link.get_text(strip=True) for link in links[1:]]
            return ' > '.join(path_parts) if path_parts else None
        return None

    def scrape_categories(self, url: Optional[str] = None) -> None:
        """Recursively scrape category pages"""
        if url is None:
            url = self.start_url
            print(f"Starting with URL: {url}")  # Debug print
            
        if url in self.visited_urls:
            return
            
        self.visited_urls.add(url)
        print(f"Downloading page: {url}")  # Debug print
        
        content = self.downloader.download_page(url)
        if not content:
            print(f"Failed to download page: {url}")  # Debug print
            return
            
        print(f"Successfully downloaded page: {url}")  # Debug print
        soup = BeautifulSoup(content, 'html.parser')

        category_path = self.extract_breadcrumb_path(soup)
        if category_path:
            self.categories.add(category_path)
            print(f"Found category: {category_path}")

        sidebar = soup.find('div', class_='sidebar--categories-navigation')
        if sidebar:
            subcategory_links = sidebar.find_all('a', class_='navigation--link')
            print(f"Found {len(subcategory_links)} subcategory links")  # Debug print
            for link in subcategory_links:
                href = link.get('href', '')
                if '/online-bestellen/alle-produkte/' in href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in self.visited_urls:
                        self.scrape_categories(full_url)

    def save_categories(self) -> None:
        """Save scraped categories to files"""
        print("Attempting to save categories...")  # Debug print
        if not self.categories:
            print("No categories found!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_file = self.config_dir / 'categories.json'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        categories_data = {
            "total_categories": len(self.categories),
            "categories": sorted(self.categories, key=lambda x: (len(x.split(' > ')), x)),
            "scrape_date": datetime.now().isoformat()
        }
        
        print(f"Writing to file: {config_file}")  # Debug print
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(categories_data, f, indent=4, ensure_ascii=False)

        print(f"\nFound {len(self.categories)} categories")
        print(f"Saved to {config_file}")

def main():
    """Run category scraper"""
    print("Starting main function...")  # Debug print
    try:
        print("Creating CategoryScraper instance...")  # Debug print
        scraper = CategoryScraper()
        print("Starting category scraping...")  # Debug print
        scraper.scrape_categories()
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debug print
        raise e
    except KeyboardInterrupt:
        print("\nScraping interrupted by user...")
    finally:
        print("Saving categories...")  # Debug print
        scraper.save_categories()

if __name__ == "__main__":
    main()