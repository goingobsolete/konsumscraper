from pathlib import Path
import json
import time
import random
import logging
from typing import List, Optional, Tuple
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

from .page_downloader import PageDownloader
from .product_models import Product, NutritionInfo, NutrientValue, serialize_product

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductScraper:
    """Scrapes product information from selected categories"""
    
    def __init__(self):
        """Initialize the product scraper with configuration and dependencies"""
        self.base_url = 'https://www.konsum-leipzig.de'
        self.config_dir = Path(__file__).parent.parent / 'config'
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.downloader = PageDownloader()
        self.selected_categories = self._load_selected_categories()
        self.products_cache = {}  # Cache to avoid re-scraping same products
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_selected_categories(self) -> List[str]:
        """Load selected categories from preferences file"""
        prefs_file = self.config_dir / 'category_preferences.json'
        if not prefs_file.exists():
            raise FileNotFoundError("Category preferences file not found")
            
        with open(prefs_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('selected_categories', [])

    def _get_category_url(self, category_path: str) -> str:
        """Convert category path to URL"""
        try:
            # Remove "Alle Produkte > " prefix and convert to URL path
            category_parts = category_path.replace("Alle Produkte > ", "").split(" > ")
            url_path = "/".join(quote(part.lower()) for part in category_parts)
            return f"{self.base_url}/online-bestellen/alle-produkte/{url_path}/"
        except Exception as e:
            logger.error(f"Error generating URL for category {category_path}: {str(e)}")
            raise

    def _extract_product_urls(self, category_page: str) -> List[str]:
        """Extract product URLs from category page"""
        product_links = []
        try:
            soup = BeautifulSoup(category_page, 'html.parser')
            
            # Find product grid or list
            product_container = soup.find('div', class_='listing--container')
            if product_container:
                for link in product_container.find_all('a', class_='product--image'):
                    href = link.get('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        product_links.append(full_url)
                        
            return product_links
        except Exception as e:
            logger.error(f"Error extracting product URLs: {str(e)}")
            return []

    def _parse_value_and_unit(self, value_str: str) -> NutrientValue:
        """Parse value and unit from string, handling German number format"""
        try:
            # Split into value and unit
            parts = value_str.strip().split()
            if not parts:
                return NutrientValue()
                
            # Handle values with units
            numeric_str = parts[0].replace(',', '.')
            unit = parts[1] if len(parts) > 1 else None
            
            # Convert to float
            value = float(numeric_str)
            return NutrientValue(value=value, unit=unit)
        except (ValueError, IndexError) as e:
            logger.debug(f"Error parsing value and unit from '{value_str}': {str(e)}")
            return NutrientValue()
    def _extract_price_info(self, soup: BeautifulSoup) -> Tuple[float, Optional[float], str]:
        """Extract price, unit price and unit from product page"""
        price = 0.0
        unit_price = None
        unit = ""
        
        try:
            price_container = soup.find('span', class_='price--content')
            if price_container:
                price_text = price_container.text.strip()
                price = float(price_text.replace('€', '').replace(',', '.').strip())

            unit_price_container = soup.find('div', class_='price--unit')
            if unit_price_container:
                # Example: "(3,98 € / 100g)"
                unit_text = unit_price_container.text.strip()
                price_part = unit_text[unit_text.find("(")+1:unit_text.find("€")].strip()
                unit = unit_text[unit_text.find("/")+1:unit_text.find(")")].strip()
                unit_price = float(price_part.replace(',', '.'))
        except Exception as e:
            logger.error(f"Error extracting price info: {str(e)}")

        return price, unit_price, unit

    def _extract_nutrition_info(self, soup: BeautifulSoup) -> NutritionInfo:
        """Extract and parse nutritional information from product page"""
        nutrition = NutritionInfo()
        
        try:
            nutrition_table = soup.find('table', class_='product--nutritional-info-table')
            if nutrition_table:
                rows = nutrition_table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        nutrient = cols[0].text.strip().lower()
                        value = cols[1].text.strip()
                        nutrition.raw_values[nutrient] = value
                        
                        # Parse specific nutrients
                        if 'portion' in nutrient or 'serving' in nutrient:
                            nutrition.serving_size = value
                        elif 'energie' in nutrient or 'energy' in nutrient:
                            if 'kcal' in value.lower():
                                nutrition.energy_kcal = self._parse_value_and_unit(value.split('kcal')[0])
                            elif 'kj' in value.lower():
                                nutrition.energy_kj = self._parse_value_and_unit(value.split('kj')[0])
                        elif 'fett' in nutrient or 'fat' in nutrient:
                            if 'davon' in nutrient or 'saturated' in nutrient:
                                nutrition.fat_saturated = self._parse_value_and_unit(value)
                            else:
                                nutrition.fat_total = self._parse_value_and_unit(value)
                        elif 'kohlenhydrate' in nutrient or 'carbohydrate' in nutrient:
                            if 'zucker' in nutrient or 'sugar' in nutrient:
                                nutrition.carbohydrates_sugar = self._parse_value_and_unit(value)
                            else:
                                nutrition.carbohydrates_total = self._parse_value_and_unit(value)
                        elif 'protein' in nutrient or 'eiweiß' in nutrient:
                            nutrition.protein = self._parse_value_and_unit(value)
                        elif 'salz' in nutrient or 'salt' in nutrient:
                            nutrition.salt = self._parse_value_and_unit(value)
                        elif 'ballaststoffe' in nutrient or 'fiber' in nutrient:
                            nutrition.fiber = self._parse_value_and_unit(value)
        except Exception as e:
            logger.error(f"Error extracting nutrition info: {str(e)}")
            
        return nutrition

    def _parse_product_page(self, html: str, url: str, category_path: str) -> Optional[Product]:
        """Parse product page HTML and extract information"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract basic product info
            name_elem = soup.find('h1', class_='product--title')
            if not name_elem:
                logger.warning(f"No product title found for {url}")
                return None
                
            product_id = url.split('/')[-1]  # Use last part of URL as ID
            name = name_elem.text.strip()
            price, unit_price, unit = self._extract_price_info(soup)
            
            # Extract description and ingredients
            description = None
            description_elem = soup.find('div', class_='product--description')
            if description_elem:
                description = description_elem.text.strip()
                
            ingredients = None
            ingredients_elem = soup.find('div', class_='product--ingredients')
            if ingredients_elem:
                ingredients = ingredients_elem.text.strip()
                
            # Extract allergens
            allergens = []
            allergens_elem = soup.find('div', class_='product--allergens')
            if allergens_elem:
                allergens = [a.strip() for a in allergens_elem.text.split(',')]
                
            # Create product object
            return Product(
                id=product_id,
                url=url,
                name=name,
                price=price,
                unit_price=unit_price,
                unit=unit,
                category_path=category_path,
                description=description,
                ingredients=ingredients,
                nutrition=self._extract_nutrition_info(soup),
                allergens=allergens,
                scrape_date=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error parsing product page {url}: {str(e)}")
            return None

    def _rate_limited_request(self, url: str) -> Optional[str]:
        """Make rate-limited request with exponential backoff"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Random delay between requests
                time.sleep(random.uniform(1.0, 2.0))
                return self.downloader.download_page(url)
            except Exception as e:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Request failed, waiting {wait_time:.2f}s: {str(e)}")
                time.sleep(wait_time)
                if attempt == max_retries - 1:
                    logger.error(f"Max retries reached for {url}")
        return None

    def scrape_category(self, category_path: str) -> List[Product]:
        """Scrape all products from a category"""
        products = []
        try:
            category_url = self._get_category_url(category_path)
            logger.info(f"Scraping category: {category_path}")
            
            page_content = self._rate_limited_request(category_url)
            if not page_content:
                logger.error(f"Failed to download category page: {category_url}")
                return products
                
            # Extract product URLs
            product_urls = self._extract_product_urls(page_content)
            logger.info(f"Found {len(product_urls)} products")
            
            # Scrape each product
            for url in product_urls:
                if url in self.products_cache:
                    products.append(self.products_cache[url])
                    continue
                    
                logger.info(f"Scraping product: {url}")
                product_html = self._rate_limited_request(url)
                if not product_html:
                    continue
                    
                product = self._parse_product_page(product_html, url, category_path)
                if product:
                    products.append(product)
                    self.products_cache[url] = product
                
        except Exception as e:
            logger.error(f"Error scraping category {category_path}: {str(e)}")
            
        return products

    def save_products(self, products: List[Product]) -> None:
        """Save scraped products to JSON file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.data_dir / f'products_{timestamp}.json'
            
            # Convert products to dictionary format using helper function
            products_data = [serialize_product(p) for p in products]
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total_products': len(products_data),
                    'scrape_date': datetime.now().isoformat(),
                    'products': products_data
                }, f, indent=4, ensure_ascii=False)
                
            logger.info(f"\nSaved {len(products_data)} products to {output_file}")
                
        except Exception as e:
            logger.error(f"Error saving products: {str(e)}")

    def scrape_all_selected_categories(self, test_mode: bool = False) -> None:
        """
        Scrape products from all selected categories
        Args:
            test_mode: If True, only scrape first category as a test
        """
        all_products = []
        
        # In test mode, just take first category
        categories = self.selected_categories[:1] if test_mode else self.selected_categories
        
        logger.info(f"Starting scrape of {len(categories)} categories...")
        
        try:
            for category in categories:
                logger.info(f"\nProcessing category: {category}")
                products = self.scrape_category(category)
                logger.info(f"Found {len(products)} products in category")
                all_products.extend(products)
                
                # Add a small delay between categories
                if len(categories) > 1:
                    logger.info("Waiting before next category...")
                    time.sleep(2)
                
            logger.info(f"\nTotal products found: {len(all_products)}")
            self.save_products(all_products)
            
        except Exception as e:
            logger.error(f"Error during category scraping: {str(e)}")
            # Still try to save what we have
            if all_products:
                self.save_products(all_products)


def main():
    """Run product scraper"""
    try:
        scraper = ProductScraper()
        # Run in test mode (just first category)
        logger.info("Running in test mode (first category only)")
        scraper.scrape_all_selected_categories(test_mode=True)
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    except KeyboardInterrupt:
        logger.info("\nScraping interrupted by user")


if __name__ == "__main__":
    main()