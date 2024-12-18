import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib.parse import urljoin

class KonsumCategoryScraper:
    def __init__(self):
        self.base_url = 'https://www.konsum-leipzig.de'
        self.start_url = f"{self.base_url}/online-bestellen/alle-produkte/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.categories = set()
        self.visited_urls = set()

    def extract_breadcrumb_path(self, soup):
        """Extract category path from breadcrumbs"""
        breadcrumb = soup.find('nav', class_='content--breadcrumb')
        if breadcrumb:
            links = breadcrumb.find_all('a', class_='breadcrumb--link')
            # Skip the "Online bestellen" part and get the rest of the path
            path_parts = [link.get_text(strip=True) for link in links[1:]]
            return ' > '.join(path_parts) if path_parts else None
        return None

    def scrape_categories(self, url=None):
        if url is None:
            url = self.start_url
            
        if url in self.visited_urls:
            return
            
        self.visited_urls.add(url)
        
        try:
            print(f"Checking: {url}")
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

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

        except requests.RequestException as e:
            print(f"Error accessing {url}: {e}")

    def save_categories(self):
        if not self.categories:
            print("No categories found!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sort categories by depth and alphabetically
        sorted_categories = sorted(self.categories, 
                                 key=lambda x: (len(x.split(' > ')), x))

        # Save as JSON
        json_file = f'konsum_categories_{timestamp}.json'
        data = {
            "total_categories": len(sorted_categories),
            "categories": sorted_categories,
            "scrape_date": datetime.now().isoformat()
        }
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Save as text
        txt_file = f'konsum_categories_{timestamp}.txt'
        with open(txt_file, 'w', encoding='utf-8') as f:
            for category in sorted_categories:
                f.write(f"{category}\n")

        print(f"\nFound {len(sorted_categories)} categories")
        print(f"Saved to {json_file} and {txt_file}")

if __name__ == "__main__":
    try:
        print("Starting category scraper...")
        scraper = KonsumCategoryScraper()
        scraper.scrape_categories()
    except KeyboardInterrupt:
        print("\nScraping interrupted by user...")
    finally:
        scraper.save_categories()