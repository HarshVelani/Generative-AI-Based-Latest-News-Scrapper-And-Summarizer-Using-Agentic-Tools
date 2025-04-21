# import time
# from typing import Dict
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# def scrape_news_article_with_selenium(url: str) -> Dict:
#     try:
#         # Set up Selenium WebDriver with headless option and other settings
#         options = Options()
#         options.add_argument('--headless')  # Run in headless mode (no UI)
#         options.add_argument('--disable-gpu')  # Disable GPU acceleration
#         options.add_argument('--no-sandbox')  # Disable sandboxing for better compatibility

#         # Set up the driver using WebDriver Manager
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#         # Open the URL
#         driver.get(url)

#         # Wait for the page to fully load and find elements (adjust XPath or other strategies)
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.TAG_NAME, "body"))
#         )

#         # Print the page source for debugging to see if content is present
#         page_source = driver.page_source
#         if "no content" in page_source.lower():
#             print("No content found in the page source.")

#         # Extract content
#         title = driver.title.strip() if driver.title else "Untitled"
#         paragraphs = driver.find_elements(By.TAG_NAME, 'p')
#         text = ' '.join([p.text for p in paragraphs if p.text])

#         # Check if text is empty and print page source for debugging
#         if not text:
#             print(f"Empty content. Page source:\n{page_source}")

#         # Extract metadata (date, source) from the page if possible
#         publish_date = "Unknown"
#         source = url.split('/')[2] if url else "Unknown"
        
#         # Example: Getting date (adjust XPath based on the page structure)
#         date_elements = driver.find_elements(By.XPATH, "//time")
#         if date_elements:
#             publish_date = date_elements[0].text.strip()

#         # Return extracted data
#         return {
#             "title": title,
#             "text": text,
#             "snippet": text[:300],  # First 300 chars as a snippet
#             "publish_date": publish_date,
#             "source": source,
#             "url": url
#         }

#     except Exception as e:
#         print(f"Error scraping {url}: {e}")
#         return None
#     finally:
#         # Close the driver after scraping
#         driver.quit()

# # Example usage
# url = "https://www.msn.com/en-xl/news/other/this-is-narendra-modi-s-vendetta-politics-congress-supriya-shrinate-on-ed-s-chargesheet-against-gandhis/ar-AA1D11tf"
# scraped_data = scrape_news_article_with_selenium(url)
# if scraped_data:
#     print(scraped_data)


# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# import os

# def download_html_and_scrape(url: str) -> dict:
#     try:
#         # Set up Selenium WebDriver (Chrome in headless mode)
#         options = webdriver.ChromeOptions()
#         options.add_argument('--headless')  # Run in headless mode (no UI)
#         options.add_argument('--disable-gpu')  # Disable GPU acceleration

#         # Set up the driver using WebDriver Manager
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#         # Open the URL
#         driver.get(url)

#         # Wait for the page to fully load (can adjust time if needed)
#         time.sleep(5)  # Adjust the sleep time based on your internet speed and page load time

#         # Get the page source after JavaScript is executed
#         page_source = driver.page_source

#         # Save the page source (HTML) to a local file
#         with open(download_path, 'w', encoding='utf-8') as file:
#             file.write(page_source)

#         # Close the driver after saving the page source
#         driver.quit()

#         # Now, read the saved HTML file to parse it
#         with open(download_path, 'r', encoding='utf-8') as file:
#             soup = BeautifulSoup(file, 'html.parser')

#         # Extract the title of the page
#         title = soup.title.string.strip() if soup.title else "Untitled"

#         # Extract all paragraph texts from the page
#         paragraphs = soup.find_all('p')
#         text = ' '.join([p.get_text() for p in paragraphs if p.get_text()])

#         # Extract the source from the URL
#         source = url.split('/')[2] if url else "Unknown"

#         # Extract publish date from <time> tag (common for many articles)
#         publish_date = "Unknown"
#         date_element = soup.find('time')
#         if date_element:
#             publish_date = date_element.get_text().strip()

#         # Return the extracted data as a dictionary
#         return {
#             "title": title,
#             "text": text,
#             "snippet": text[:300],  # First 300 characters as a snippet
#             "publish_date": publish_date,
#             "source": source,
#             "url": url
#         }

#     except Exception as e:
#         print(f"Error downloading and scraping {url}: {e}")
#         return None

# # Example usage
# url = "https://www.techtarget.com/searchenterpriseai/news/366622996/Whats-new-and-not-new-with-OpenAIs-latest-reasoning-models"
# download_path = "downloaded_page.html"  # Path to save the HTML file locally
# scraped_data = download_html_and_scrape(url, download_path)
# if scraped_data:
#     import json

#     # Input data (JSON string, cleaned up from your provided output)
#     print(type(scraped_data))
    

#     # Input data (Python dictionary)
#     input_data = scraped_data

#     # Extract variables from the dictionary
#     title = input_data.get('title', 'N/A')
#     text = input_data.get('text', 'N/A')
#     snippet = input_data.get('snippet', 'N/A')
#     publish_date = input_data.get('publish_date', 'N/A')
#     source = input_data.get('source', 'N/A')
#     url = input_data.get('url', 'N/A')

#     # Truncate text for display purposes (full text is still available in the variable)
#     text_preview = text + '...' if len(text) > 500 else text

#     # Structured output format
#     output_template = """
#     === Structured Article Information ===
#     Title: {title}
#     Source: {source}
#     Publish Date: {publish_date}
#     URL: {url}
#     Snippet: {snippet}
#     Text Preview: {text_preview}
#     ====================================
#     """

#     # Print the structured output
#     print(output_template.format(
#         title=title,
#         source=source,
#         publish_date=publish_date,
#         url=url,
#         snippet=snippet,
#         text_preview=text_preview
#     ))














import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scrape_url(url: str) -> dict:
    try:
        # Set up Selenium WebDriver (Chrome in headless mode)
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode (no UI)
        chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration

        # Set up the driver using WebDriver Manager
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # Open the URL
        driver.get(url)

        # Wait for the page to fully load (can adjust time if needed)
        time.sleep(5)  # Adjust the sleep time based on your internet speed and page load time

        # Get the page source after JavaScript is executed
        page_source = driver.page_source

        # Close the driver
        driver.quit()

        # Parse the page source directly with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract the title of the page
        title = soup.title.string.strip() if soup.title else "Untitled"

        # Extract all paragraph texts from the page
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs if p.get_text()])

        # Extract the source from the URL
        source = url.split('/')[2] if url else "Unknown"

        # Extract publish date from <time> tag (common for many articles)
        publish_date = "Unknown"
        date_element = soup.find('time')
        if date_element:
            publish_date = date_element.get_text().strip()

        # Return the extracted data as a dictionary
        return {
            "title": title,
            "text": text,
            "snippet": text,  # First 300 characters as a snippet
            "publish_date": publish_date,
            "source": source,
            "url": url
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

# Example usage
# https://www.techtarget.com/searchenterpriseai/news/366622996/Whats-new-and-not-new-with-OpenAIs-latest-reasoning-models

url = "https://www.techtarget.com/searchenterpriseai/news/366622996/Whats-new-and-not-new-with-OpenAIs-latest-reasoning-models"
scraped_data = scrape_url(url)
if scraped_data:
    # Extract variables from the dictionary
    title = scraped_data.get('title', 'N/A')
    text = scraped_data.get('text', 'N/A')
    snippet = scraped_data.get('snippet', 'N/A')
    publish_date = scraped_data.get('publish_date', 'N/A')
    source = scraped_data.get('source', 'N/A')
    url = scraped_data.get('url', 'N/A')

    # Truncate text for display purposes (full text is still available in the variable)
    text_preview = text + '...' if len(text) > 500 else text

    # Structured output format
    output_template = """
    === Structured Article Information ===
    Title: {title}
    Source: {source}
    Publish Date: {publish_date}
    URL: {url}
    Snippet: {snippet}
    Text Preview: {text_preview}
    ====================================
    """

    # Print the structured output
    print(output_template.format(
        title=title,
        source=source,
        publish_date=publish_date,
        url=url,
        snippet=snippet,
        text_preview=text_preview
    ))
















# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from typing import Dict, Optional, List
# import random
# import time

# # Configuration
# DEFAULT_HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Referer': 'https://www.google.com/',
#     'DNT': '1'
# }

# # List of free proxies (replace with your own proxy list or paid service)
# PROXY_LIST = [
#     "103.156.17.63:3128",
#     "45.95.147.106:8080",
#     "45.95.147.99:8080",
#     "45.95.147.105:8080",
#     "45.95.147.97:8080",
#     "45.95.147.98:8080",
#     "45.95.147.100:8080",
#     "45.95.147.101:8080",
#     "45.95.147.102:8080",
#     "45.95.147.103:8080"
# ]

# def get_random_proxy() -> Dict:
#     """Get a random proxy from the list"""
#     proxy = random.choice(PROXY_LIST)
#     return {
#         'http': f'http://{proxy}',
#         'https': f'http://{proxy}'
#     }

# def test_proxy(proxy: Dict) -> bool:
#     """Test if a proxy is working"""
#     try:
#         response = requests.get(
#             "http://httpbin.org/ip",
#             proxies=proxy,
#             timeout=10
#         )
#         return response.status_code == 200
#     except:
#         return False

# def get_working_proxy(max_attempts: int = 5) -> Optional[Dict]:
#     """Get a working proxy with retries"""
#     for _ in range(max_attempts):
#         proxy = get_random_proxy()
#         if test_proxy(proxy):
#             return proxy
#         time.sleep(1)
#     return None

# def setup_selenium_driver(proxy: Optional[Dict] = None) -> webdriver.Chrome:
#     """Configure Selenium WebDriver with proxy support"""
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument(f"user-agent={DEFAULT_HEADERS['User-Agent']}")
    
#     if proxy:
#         proxy_url = proxy['http'].replace('http://', '')
#         chrome_options.add_argument(f'--proxy-server={proxy_url}')
    
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     return driver

# def extract_with_proxy(url: str, method: str = "requests", proxy: Optional[Dict] = None) -> Optional[Dict]:
#     """Extract content using specified method with proxy support"""
#     try:
#         if method == "selenium":
#             driver = setup_selenium_driver(proxy)
#             driver.get(url)
#             driver.implicitly_wait(10)
#             html = driver.page_source
#             driver.quit()
#         else:
#             response = requests.get(
#                 url,
#                 headers=DEFAULT_HEADERS,
#                 proxies=proxy,
#                 timeout=20
#             )
#             html = response.text
        
#         soup = BeautifulSoup(html, 'html.parser')
        
#         # Clean up the HTML
#         for element in soup(['script', 'style', 'iframe', 'nav', 'footer', 'aside']):
#             element.decompose()
        
#         # Extract title
#         title = soup.title.string.strip() if soup.title else url.split('/')[2]
        
#         # Extract main content
#         article_body = (soup.find('article') or 
#                        soup.find('main') or 
#                        soup.find('div', class_=lambda x: x and 'content' in x.lower()) or
#                        soup.find('div', id=lambda x: x and 'content' in x.lower()))
        
#         if article_body:
#             text = ' '.join([p.get_text().strip() for p in article_body.find_all(['p', 'h1', 'h2', 'h3'])])
#         else:
#             text = ' '.join([p.get_text().strip() for p in soup.find_all('p')])
        
#         text = text.strip()
#         if not text or len(text) < 100:
#             return None
        
#         source = url.split('/')[2].replace('www.', '')
#         snippet = text[:300] + '...' if len(text) > 300 else text
        
#         return {
#             "title": title,
#             "text": text,
#             "snippet": snippet,
#             "publish_date": "Unknown",
#             "source": source,
#             "url": url
#         }
        
#     except Exception as e:
#         print(f"Extraction failed with {method} method: {e}")
#         return None

# def scrape_news_article_with_proxy(url: str) -> Optional[Dict]:
#     """Main scraping function with proxy rotation and multiple methods"""
#     methods = ["requests", "selenium"]
#     proxy = get_working_proxy()
    
#     if not proxy:
#         print("Warning: No working proxy found, trying without proxy")
    
#     for method in methods:
#         result = extract_with_proxy(url, method, proxy)
#         if result:
#             return result
#         time.sleep(2)  # Delay between attempts
    
#     # Final attempt without proxy if all else fails
#     print("All proxy methods failed, trying direct connection")
#     for method in methods:
#         result = extract_with_proxy(url, method, None)
#         if result:
#             return result
#         time.sleep(2)
    
#     return None

# # Test the function
# if __name__ == "__main__":
#     test_urls = [
#         "https://www.techtarget.com/searchenterpriseai/news/366622996/Whats-new-and-not-new-with-OpenAIs-latest-reasoning-models"
#         # "https://www.bbc.com/news/world-us-canada-68840189",
#         # "https://www.wsj.com/livecoverage/stock-market-trump-tariffs-trade-war-04-16-25"
#     ]
    
#     for url in test_urls:
#         print(f"\nScraping: {url}")
#         result = scrape_news_article_with_proxy(url)
#         if result:
#             print(f"Success! Title: {result['title']}")
#             print(f"Snippet: {result['snippet']}")
#         else:
#             print("Failed to scrape article")

