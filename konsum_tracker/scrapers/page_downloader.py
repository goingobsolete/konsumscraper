import requests
from pathlib import Path

def download_page_html(url, output_file='page.html'):
    """
    Downloads the HTML content from a URL and saves it to a file.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        Path(output_file).write_text(response.text, encoding='utf-8')
        print(f"Successfully downloaded HTML to {output_file}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the page: {e}")
        return None

# Test with a Konsum Leipzig product page
url = "https://www.konsum-leipzig.de/online-bestellen/alle-produkte/tiefkuehlprodukte/obst-gemuese/20163/alnatura-bio-sauerkirschen-300-g?c=216"
download_page_html(url, "product_page.html")