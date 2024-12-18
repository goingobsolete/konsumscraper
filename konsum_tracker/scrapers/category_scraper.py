from bs4 import BeautifulSoup
from datetime import datetime
import json
from urllib.parse import urljoin
from typing import Set, Optional
from pathlib import Path

from .page_downloader import PageDownloader

class CategoryScraper:
    def __init__(self):
        self.base_url = 'https://www.konsum-leipzig.de'
        self.start_url = f"{self.base_url}/online-bestellen/alle-produkte/"
        self.categories = set()
        self.visited_urls = set()
        self.downloader = PageDownloader()
        # Get the path to the config directory
        self.config_dir = Path(__file__).parent.parent / 'config'

    # ... (rest of the methods stay the same until save_categories)

    def save_categories(self) -> None:
        """Save scraped categories to files"""
        if not self.categories:
            print("No categories found!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use absolute path for config file
        config_file = self.config_dir / 'categories.json'
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        categories_data = {
            "total_categories": len(self.categories),
            "categories": sorted(self.categories, key=lambda x: (len(x.split(' > ')), x)),
            "scrape_date": datetime.now().isoformat()
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(categories_data, f, indent=4, ensure_ascii=False)

        print(f"\nFound {len(self.categories)} categories")
        print(f"Saved to {config_file}")

# ... (rest of the file stays the same)