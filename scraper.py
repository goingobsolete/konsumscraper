from bs4 import BeautifulSoup

class KonsumScraper:
    def __init__(self, html_file):
        """
        Initialize the scraper with an HTML file
        
        :param html_file: Path to the HTML file
        """
        with open(html_file, 'r', encoding='utf-8') as file:
            self.soup = BeautifulSoup(file, 'html.parser')

    def extract_product_name(self):
        """
        Extract the product name from the page
        
        :return: Product name or None
        """
        name_elem = self.soup.find('h1', class_='product--title')
        return name_elem.text.strip() if name_elem else None

    def extract_price(self):
        """
        Extract the product price
        
        :return: Price as a string or None
        """
        price_elem = self.soup.find('span', class_='price--content')
        return price_elem.text.strip() if price_elem else None

# Example usage
if __name__ == "__main__":
    scraper = KonsumScraper('product_page.html')
    
    print("Product Name:", scraper.extract_product_name())
    print("Price:", scraper.extract_price())