import requests
from pathlib import Path
from typing import Optional

class PageDownloader:
    """Downloads and manages web pages from Konsum Leipzig"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def download_page(self, url: str, save_to_file: Optional[str] = None) -> Optional[str]:
        """
        Downloads the HTML content from a URL and optionally saves it to a file.
        
        Args:
            url: The URL to download
            save_to_file: Optional filename to save the HTML content
            
        Returns:
            The page content as string if successful, None if failed
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            content = response.text
            
            if save_to_file:
                Path(save_to_file).write_text(content, encoding='utf-8')
                print(f"Successfully downloaded HTML to {save_to_file}")
            
            return content
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading the page: {e}")
            return None

    def download_product_page(self, product_url: str, save_to_file: Optional[str] = None) -> Optional[str]:
        """
        Specialized method for downloading product pages with validation.
        
        Args:
            product_url: The product page URL
            save_to_file: Optional filename to save the HTML content
            
        Returns:
            The page content as string if successful, None if failed
        """
        if not 'konsum-leipzig.de' in product_url:
            print("Error: URL must be from konsum-leipzig.de")
            return None
            
        return self.download_page(product_url, save_to_file)

def main():
    """Test functionality with a sample product page"""
    downloader = PageDownloader()
    test_url = "https://www.konsum-leipzig.de/online-bestellen/alle-produkte/tiefkuehlprodukte/obst-gemuese/20163/alnatura-bio-sauerkirschen-300-g"
    content = downloader.download_product_page(test_url, "test_product.html")
    if content:
        print("Successfully downloaded test product page")

if __name__ == "__main__":
    main()