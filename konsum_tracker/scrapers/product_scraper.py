from pathlib import Path
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

from .page_downloader import PageDownloader

@dataclass
class NutrientValue:
    """Data class for a nutrient value with its unit"""
    value: Optional[float] = None
    unit: Optional[str] = None

@dataclass
class NutritionInfo:
    """Data class for nutrition information with separate value and unit storage"""
    serving_size: Optional[str] = None
    energy_kcal: Optional[NutrientValue] = None
    energy_kj: Optional[NutrientValue] = None
    fat_total: Optional[NutrientValue] = None
    fat_saturated: Optional[NutrientValue] = None
    carbohydrates_total: Optional[NutrientValue] = None
    carbohydrates_sugar: Optional[NutrientValue] = None
    protein: Optional[NutrientValue] = None
    salt: Optional[NutrientValue] = None
    fiber: Optional[NutrientValue] = None
    raw_values: Dict[str, str] = None  # Store original unparsed values

@dataclass
class Product:
    """Data class to store product information"""
    id: str
    url: str
    name: str
    price: float
    unit_price: Optional[float]
    unit: str
    category_path: str
    description: Optional[str]
    ingredients: Optional[str]
    nutrition: NutritionInfo
    allergens: List[str]
    scrape_date: datetime

class ProductScraper:
    """Scrapes product information from selected categories"""
    
    def __init__(self):
        self.base_url = 'https://www.konsum-leipzig.de'
        self.config_dir = Path(__file__).parent.parent / 'config'
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.downloader = PageDownloader()
        self.selected_categories = self._load_selected_categories()
        self.products_cache = {}  # Cache to avoid re-scraping same products
        
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
        # Remove "Alle Produkte > " prefix and convert to URL path
        category_parts = category_path.replace("Alle Produkte > ", "").split(" > ")
        url_path = "/".join(quote(part.lower()) for part in category_parts)
        return f"{self.base_url}/online-bestellen/alle-produkte/{url_path}/"

    def _extract_product_urls(self, category_page: str) -> List[str]:
        """Extract product URLs from category page"""
        soup = BeautifulSoup(category_page, 'html.parser')
        product_links = []
        
        # Find product grid or list
        product_container = soup.find('div', class_='listing--container')
        if product_container:
            for link in product_container.find_all('a', class_='product--image'):
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    product_links.append(full_url)
                    
        return product_links

    def _extract_price_info(self, soup: BeautifulSoup) -> tuple[float, Optional[float], str]:
        """Extract price, unit price and unit from product page"""
        price = 0.0
        unit_price = None
        unit = ""
        
        price_container = soup.find('span', class_='price--content')
        if price_container:
            price_text = price_container.text.strip()
            try:
                price = float(price_text.replace('€', '').replace(',', '.').strip())
            except ValueError:
                print(f"Error parsing price: {price_text}")

        unit_price_container = soup.find('div', class_='price--unit')
        if unit_price_container:
            # Example: "(3,98 € / 100g)"
            unit_text = unit_price_container.text.strip()
            try:
                price_part = unit_text[unit_text.find("(")+1:unit_text.find("€")].strip()
                unit = unit_text[unit_text.find("/")+1:unit_text.find(")")].strip()
                unit_price = float(price_part.replace(',', '.'))
            except (ValueError, IndexError):
                print(f"Error parsing unit price: {unit_text}")

        return price, unit_price, unit

    def _parse_value_with_unit(self, value_str: str) -> tuple[Optional[float], Optional[str]]:
        """
        Parse value and unit from string, handling German number format
        Returns tuple of (numeric_value, unit)
        """
        try:
            # Split into value and unit
            parts = value_str.strip().split()
            if not parts:
                return None, None
                
            # Handle values with units
            numeric_str = parts[0].replace(',', '.')
            unit = parts[1] if len(parts) > 1 else None
            
            # Convert to float
            value = float(numeric_str)
            return value, unit
        except (ValueError, IndexError):
            return None, None
            
    def _parse_value_and_unit(self, value_str: str) -> NutrientValue:
        """
        Parse value and unit from string, handling German number format
        Returns NutrientValue with separated numeric value and unit
        """
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
        except (ValueError, IndexError):
            return NutrientValue()

nutrition.energy_kcal = self._parse_numeric_value(value)
                        elif 'kj' in value.lower():
                            nutrition.energy_kj = self._parse_numeric_value(value)
                    elif 'fett' in nutrient or 'fat' in nutrient:
                        if 'davon' in nutrient or 'saturated' in nutrient:
                            nutrition.fat_saturated = self._parse_numeric_value(value)
                        else:
                            nutrition.fat_total = self._parse_numeric_value(value)
                    elif 'kohlenhydrate' in nutrient or 'carbohydrate' in nutrient:
                        if 'zucker' in nutrient or 'sugar' in nutrient:
                            nutrition.carbohydrates_sugar = self._parse_numeric_value(value)
                        else:
                            nutrition.carbohydrates_total = self._parse_numeric_value(value)
                    elif 'protein' in nutrient or 'eiweiß' in nutrient:
                        nutrition.protein = self._parse_numeric_value(value)
                    elif 'salz' in nutrient or 'salt' in nutrient:
                        nutrition.salt = self._parse_numeric_value(value)
                    elif 'ballaststoffe' in nutrient or 'fiber' in nutrient:
                        nutrition.fiber = self._parse_numeric_value(value)
        
        nutrition.raw_values = raw_values
        return nutrition

    def _parse_product_page(self, html: str, url: str, category_path: str) -> Optional[Product]:
        """Parse product page HTML and extract information"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract basic product info
        name_elem = soup.find('h1', class_='product--title')
        if not name_elem:
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

    def scrape_category(self, category_path: str) -> List[Product]:
        """Scrape all products from a category"""
        products = []
        category_url = self._get_category_url(category_path)
        
        print(f"Scraping category: {category_path}")
        page_content = self.downloader.download_page(category_url)
        if not page_content:
            print(f"Failed to download category page: {category_url}")
            return products
            
        # Extract product URLs
        product_urls = self._extract_product_urls(page_content)
        print(f"Found {len(product_urls)} products")
        
        # Scrape each product
        for url in product_urls:
            if url in self.products_cache:
                products.append(self.products_cache[url])
                continue
                
            print(f"Scraping product: {url}")
            product_html = self.downloader.download_page(url)
            if not product_html:
                print(f"Failed to download product page: {url}")
                continue
                
            product = self._parse_product_page(product_html, url, category_path)
            if product:
                products.append(product)
                self.products_cache[url] = product
                
            # Be nice to the server
            time.sleep(1)
            
        return products

    def save_products(self, products: List[Product]) -> None:
        """Save scraped products to JSON file"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.data_dir / f'products_{timestamp}.json'
        
        # Convert products to dictionary format
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'url': product.url,
                'name': product.name,
                'price': product.price,
                'unit_price': product.unit_price,
                'unit': product.unit,
                'category_path': product.category_path,
                'description': product.description,
                'ingredients': product.ingredients,
                'nutrition': {
                    'serving_size': product.nutrition.serving_size,
                    'energy_kcal': {'value': product.nutrition.energy_kcal.value if product.nutrition.energy_kcal else None,
                                  'unit': product.nutrition.energy_kcal.unit if product.nutrition.energy_kcal else None},
                    'energy_kj': {'value': product.nutrition.energy_kj.value if product.nutrition.energy_kj else None,
                                'unit': product.nutrition.energy_kj.unit if product.nutrition.energy_kj else None},
                    'fat_total': {'value': product.nutrition.fat_total.value if product.nutrition.fat_total else None,
                                'unit': product.nutrition.fat_total.unit if product.nutrition.fat_total else None},
                    'fat_saturated': {'value': product.nutrition.fat_saturated.value if product.nutrition.fat_saturated else None,
                                    'unit': product.nutrition.fat_saturated.unit if product.nutrition.fat_saturated else None},
                    'carbohydrates_total': {'value': product.nutrition.carbohydrates_total.value if product.nutrition.carbohydrates_total else None,
                                          'unit': product.nutrition.carbohydrates_total.unit if product.nutrition.carbohydrates_total else None},
                    'carbohydrates_sugar': {'value': product.nutrition.carbohydrates_sugar.value if product.nutrition.carbohydrates_sugar else None,
                                          'unit': product.nutrition.carbohydrates_sugar.unit if product.nutrition.carbohydrates_sugar else None},
                    'protein': {'value': product.nutrition.protein.value if product.nutrition.protein else None,
                              'unit': product.nutrition.protein.unit if product.nutrition.protein else None},
                    'salt': {'value': product.nutrition.salt.value if product.nutrition.salt else None,
                           'unit': product.nutrition.salt.unit if product.nutrition.salt else None},
                    'fiber': {'value': product.nutrition.fiber.value if product.nutrition.fiber else None,
                            'unit': product.nutrition.fiber.unit if product.nutrition.fiber else None},
                    'raw_values': product.nutrition.raw_values
                },
                'allergens': product.allergens,
                'scrape_date': product.scrape_date.isoformat()
            })
            
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_products': len(products_data),
                'scrape_date': datetime.now().isoformat(),
                'products': products_data
            }, f, indent=4, ensure_ascii=False)
            
        print(f"\nSaved {len(products_data)} products to {output_file}")

    def scrape_all_selected_categories(self, test_mode: bool = False) -> None:
        """
        Scrape products from all selected categories
        Args:
            test_mode: If True, only scrape first category as a test
        """
        all_products = []
        
        # In test mode, just take first category
        categories = self.selected_categories[:1] if test_mode else self.selected_categories
        
        print(f"Starting scrape of {len(categories)} categories...")
        
        for category in categories:
            print(f"\nProcessing category: {category}")
            products = self.scrape_category(category)
            print(f"Found {len(products)} products")
            all_products.extend(products)
            
        self.save_products(all_products)

def main():
    """Run product scraper"""
    try:
        scraper = ProductScraper()
        # Run in test mode (just first category)
        print("Running in test mode (first category only)")
        scraper.scrape_all_selected_categories(test_mode=True)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")

if __name__ == "__main__":
    main()