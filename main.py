# DuckDuckGO Search
# import os
# import json
# import re
# from typing import Dict, List
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_groq import ChatGroq
# from langchain_community.tools import DuckDuckGoSearchResults

# # Initialize LLM (Grok model)
# llm = ChatGroq(
#     model="meta-llama/llama-4-scout-17b-16e-instruct",
#     api_key=os.getenv("GROQ_API_KEY")
# )
# if not os.getenv("GROQ_API_KEY"):
#     raise ValueError("GROQ_API_KEY not set. Set it with: export GROQ_API_KEY=your_groq_api_key")

# # DuckDuckGo news search
# def langchain_duckduckgo_search(query: str) -> List[Dict]:
#     """Search for news articles using LangChain's DuckDuckGoSearchResults."""
#     search = DuckDuckGoSearchResults(backend="news", max_results=3)
#     query_with_context = f"{query} latest news"
#     print(f"Searching DuckDuckGo for: {query_with_context}")
    
#     try:
#         results = search.invoke(query_with_context)
#         print(f"Raw results: {str(results)}...")
        

#         text = results

#         # Pattern to extract fields using non-greedy match
#         pattern = re.compile(
#             r"snippet:\s*(.*?),\s*title:\s*(.*?),\s*link:\s*(.*?),\s*date:\s*(.*?),\s*source:\s*(.*?)(?:,|$)",
#             re.DOTALL
#         )

#         # Extract matches
#         matches = pattern.findall(text)

#         # Format results
#         articles = []
#         for match in matches:
#             article = {
#                 "snippet": match[0].strip(),
#                 "title": match[1].strip(),
#                 "url": match[2].strip(),
#                 "date": match[3].strip(),
#                 "source": match[4].strip()
#             }
#             articles.append(article)

#         # Print the structured output
#         for i, article in enumerate(articles, 1):
#             print(f"\n--- Article {i} ---")
#             for key, value in article.items():
#                 print(f"{key.capitalize()}: {value}")

#         # return formatted_results
    
#     except Exception as e:
#         print(f"DuckDuckGo search error: {e}")
#         return []

# # Extract article content
# def extract_article_content(url: str) -> Dict:
#     """Extract content from a news article URL using newspaper3k."""
#     try:
#         from newspaper import Article
#         article = Article(url)
#         article.download()
#         article.parse()
        
#         if not article.text or len(article.text) < 100:
#             print(f"Article too short or empty: {url}")
#             return None
            
#         return {
#             "title": article.title or "Untitled",
#             "text": article.text[:4000],
#             "publish_date": str(article.publish_date) if article.publish_date else "Unknown",
#             "url": url
#         }
#     except Exception as e:
#         print(f"Error extracting content from {url}: {e}")
#         return None

# # Summarize article
# def summarize_article(article_data: Dict, topic: str) -> str:
#     """Summarize an article into a news piece."""
#     if not article_data:
#         return None
    
#     template = """
#     Create an SEO-optimized news summary:
    
#     ARTICLE CONTENT: {article_text}
#     TITLE: {article_title}
#     PUBLISHED: {publish_date}
#     URL: {article_url}
#     TOPIC: {topic}
    
#     REQUIREMENTS:
#     - Title: Custom, SEO-optimized
#     - Length: 300-500 words
#     - Structure: Lead paragraph, context, key facts
#     - Keywords: [KEYWORDS: relevant, keywords]
    
#     OUTPUT:
#     ## [Title]
    
#     [Summary]
    
#     **Source:** [Source Name] ([article_url])
    
#     [KEYWORDS: keyword1, keyword2]
#     """
    
#     prompt = ChatPromptTemplate.from_template(template)
#     chain = prompt | llm | StrOutputParser()
    
#     try:
#         return chain.invoke({
#             "article_text": article_data["text"],
#             "article_title": article_data["title"],
#             "publish_date": article_data["publish_date"],
#             "article_url": article_data["url"],
#             "topic": topic
#         })
#     except Exception as e:
#         print(f"Error summarizing article: {e}")
#         return None

# # def process_query(query: str) -> List[str]:
# #     """Process a query and return summarized news articles."""
# #     print(f"\nSearching for news on: {query}")
    
# #     # Search with DuckDuckGo
# #     search_results = langchain_duckduckgo_search(query)
# #     if not search_results:
# #         return ["No news articles found."]
    
# #     # Process results
# #     summaries = []
# #     for i, result in enumerate(search_results, 1):
# #         url = result.get("url")
# #         if not url:
# #             continue
        
# #         print(f"Processing article {i}/{len(search_results)}: {result.get('title', 'Unknown title')}")
        
# #         # Extract and summarize
# #         article_data = extract_article_content(url)
# #         if article_data:
# #             summary = summarize_article(article_data, query)
# #             if summary:
# #                 summaries.append(summary)
    
# #     return summaries or ["No articles could be summarized."]

# def main():
#     print("News Agent Initialized")
#     print("=====================")
    
#     while True:
#         query = input("\nEnter a topic to search for news (or 'exit' to quit): ")
#         if query.lower() == 'exit':
#             break
            
#         print("\n" + "=" * 50)
#         summaries = langchain_duckduckgo_search(query)
#         # for i, summary in enumerate(summaries, 1):
#         #     print(f"\n--- ARTICLE {i} ---\n")
#         #     print(summary)
#         #     print("\n" + "=" * 50)

# if __name__ == "__main__":
#     main()








# # DuckDuckGO Search with Summarization from snippet

# import os
# import re
# from typing import Dict, List
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_groq import ChatGroq
# from langchain_community.tools import DuckDuckGoSearchResults
# from langchain_community.document_loaders import WebBaseLoader

# # Initialize LLM (Groq model)
# llm = ChatGroq(
#     model="meta-llama/llama-4-scout-17b-16e-instruct",
#     api_key=os.getenv("GROQ_API_KEY")
# )
# if not os.getenv("GROQ_API_KEY"):
#     raise ValueError("GROQ_API_KEY not set. Set it with: export GROQ_API_KEY=your_groq_api_key")

# # DuckDuckGo news search and basic article link/title extraction
# def langchain_duckduckgo_search(query: str, max_articles: int = 1) -> List[Dict]:
#     search = DuckDuckGoSearchResults(backend="news", max_results=max_articles)
#     query_with_context = f"{query} latest news"
#     print(f"Searching DuckDuckGo for: {query_with_context}")

#     try:
#         results = search.invoke(query_with_context)
#         print(f"Raw results: {str(results)}...")

#         text = results
#         pattern = re.compile(
#             r"snippet:\s*(.*?),\s*title:\s*(.*?),\s*link:\s*(.*?),\s*date:\s*(.*?),\s*source:\s*(.*?)(?:,|$)",
#             re.DOTALL
#         )

#         matches = pattern.findall(text)

#         articles = []
#         for match in matches:
#             article = {
#                 "title": match[1].strip(),
#                 "url": match[2].strip()
#             }
#             articles.append(article)

#         return articles[:max_articles]

#     except Exception as e:
#         print(f"DuckDuckGo search error: {e}")
#         return []

# # Scrape individual news article page using LangChain Document Loader
# def scrape_news_article(url: str) -> Dict:
#     try:
#         loader = WebBaseLoader(url)
#         document = loader.load()[0]
#         text = document.page_content.strip()
#         metadata = document.metadata

#         return {
#             "title": metadata.get("title", "Untitled"),
#             "text": text,
#             "snippet": text,
#             "publish_date": metadata.get("publish_date", "Unknown"),
#             "source": url.split('/')[2],
#             "url": url
#         }
#     except Exception as e:
#         print(f"Error scraping {url}: {e}")
#         return None

# # Summarize article
# def summarize_article(article_data: Dict, topic: str) -> str:
#     if not article_data:
#         return None

#     template = """
#     Create an SEO-optimized news summary:

#     ARTICLE CONTENT: {article_text}
#     TITLE: {article_title}
#     PUBLISHED: {publish_date}
#     URL: {article_url}
#     TOPIC: {topic}

#     REQUIREMENTS:
#     - Title: Custom, SEO-optimized
#     - Length: 300-500 words
#     - Structure: Lead paragraph, context, key facts
#     - Keywords: [KEYWORDS: relevant, keywords]

#     OUTPUT:
#     ## [Title]

#     [Summary]

#     **Source:** [Source Name] ([article_url])

#     [KEYWORDS: keyword1, keyword2]
#     """

#     prompt = ChatPromptTemplate.from_template(template)
#     chain = prompt | llm | StrOutputParser()

#     try:
#         return chain.invoke({
#             "article_text": article_data["text"],
#             "article_title": article_data["title"],
#             "publish_date": article_data["publish_date"],
#             "article_url": article_data["url"],
#             "topic": topic
#         })
#     except Exception as e:
#         print(f"Error summarizing article: {e}")
#         return None


# def main():
#     print("News Agent Initialized")
#     print("=====================")

#     while True:
#         query = input("\nEnter a topic to search for news (or 'exit' to quit): ")
#         if query.lower() == 'exit':
#             break

#         try:
#             max_articles = int(input("How many articles do you want to extract and summarize? "))
#         except ValueError:
#             print("Invalid input, using default of 3 articles.")
#             max_articles = 3

#         print("\n" + "=" * 50)
#         search_results = langchain_duckduckgo_search(query, max_articles)

#         for i, result in enumerate(search_results, 1):
#             print(f"\n--- ARTICLE {i} ---")
#             scraped_data = scrape_news_article(result['url'])

#             # print("=========================== SCRAPED DATA ===========================\n", scraped_data)
#             if scraped_data:
#                 summary = summarize_article(scraped_data, query)
#                 if summary:
#                     print("=========================== SUMMARY ===========================\n", summary)
#             print("=" * 50)

# if __name__ == "__main__":
#     main()









# Google Search with Summarization
import os
import re
import requests
import time
import random
from typing import Dict, List
from bs4 import BeautifulSoup
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader

# Initialize LLM (Groq model)
llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    api_key="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"
)
# if not os.getenv("GROQ_API_KEY"):
#     raise ValueError("GROQ_API_KEY not set. Set it with: export GROQ_API_KEY=your_groq_api_key")

# Define user agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def get_random_headers():
    """Get random headers to avoid detection"""
    return {
        'User-Agent': os.getenv('USER_AGENT', random.choice(USER_AGENTS)),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }

def search_duckduckgo_news(query: str, max_results: int = 3):
    """Search news using DuckDuckGo"""
    search_url = f"https://duckduckgo.com/html/?q={query}+news"
    headers = get_random_headers()
    
    try:
        print(f"Searching DuckDuckGo for: {query}")
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Extract links from search results
        for result in soup.select('.result__a'):
            link = result.get('href')
            if link:
                # Clean up URL
                if '/l/?uddg=' in link:
                    # Extract the actual URL from DuckDuckGo's redirect
                    decoded_url = link.split('/l/?uddg=')[1].split('&')[0]
                    link = requests.utils.unquote(decoded_url)
                
                results.append({
                    "title": result.text.strip(),
                    "url": link,
                    "source": link.split('/')[2] if '//' in link else "Unknown source",
                    "snippet": ""
                })
                
                if len(results) >= max_results:
                    break
                    
        return results
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
        return []

def search_bing_news(query: str, max_results: int = 3):
    """Search news using Bing"""
    search_url = f"https://www.bing.com/news/search?q={query.replace(' ', '+')}"
    headers = get_random_headers()
    
    try:
        print(f"Searching Bing News for: {query}")
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Extract news articles
        for article in soup.select('.news-card'):
            link_element = article.select_one('a.title')
            if link_element:
                link = link_element.get('href')
                title = link_element.text.strip()
                
                source_element = article.select_one('.source')
                source = source_element.text.strip() if source_element else "Unknown"
                
                snippet_element = article.select_one('.snippet')
                snippet = snippet_element.text.strip() if snippet_element else ""
                
                if link and link.startswith('http'):
                    results.append({
                        "title": title,
                        "url": link,
                        "source": source,
                        "snippet": snippet
                    })
                    
                    if len(results) >= max_results:
                        break
        
        return results
    except Exception as e:
        print(f"Bing News search error: {e}")
        return []

def news_api_search(query: str, max_results: int = 3):
    """Search using NewsAPI if API key is available"""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("NEWS_API_KEY not set, skipping NewsAPI search")
        return []
        
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={api_key}"
    
    try:
        print(f"Searching NewsAPI for: {query}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if data["status"] == "ok" and data["totalResults"] > 0:
            for article in data["articles"][:max_results]:
                results.append({
                    "title": article["title"],
                    "url": article["url"],
                    "source": article["source"]["name"],
                    "snippet": article["description"]
                })
        return results
    except Exception as e:
        print(f"NewsAPI search error: {e}")
        return []

def search_raw_html(url: str, query: str, max_results: int = 3):
    """Extract links from raw HTML of a news site"""
    headers = get_random_headers()
    
    try:
        print(f"Searching {url} for: {query}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Find all links
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Look for links that might contain the query terms
        query_terms = query.lower().split()
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href')
            text = link.text.strip()
            
            # Skip empty links, navigation, etc.
            if (not href or not text or len(text) < 15 or 
                href.startswith('#') or 'javascript:' in href):
                continue
                
            # Make absolute URL if needed
            if href.startswith('/'):
                href = f"{url.split('//', 1)[0]}//{url.split('//', 1)[1].split('/', 1)[0]}{href}"
            elif not href.startswith(('http://', 'https://')):
                continue
                
            # Check if link text contains any query terms
            if any(term in text.lower() for term in query_terms):
                results.append({
                    "title": text,
                    "url": href,
                    "source": href.split('/')[2] if '//' in href else "Unknown",
                    "snippet": ""
                })
                
                if len(results) >= max_results:
                    break
                    
        return results
    except Exception as e:
        print(f"Raw HTML search error for {url}: {e}")
        return []

def multi_source_news_search(query: str, max_articles: int = 3) -> List[Dict]:
    """Search multiple news sources and aggregate results"""
    all_results = []
    
    # Try NewsAPI first if available
    results = news_api_search(query, max_articles)
    if results:
        print(f"Found {len(results)} results from NewsAPI")
        all_results.extend(results)
    
    # If we don't have enough results, try Bing News
    if len(all_results) < max_articles:
        remaining = max_articles - len(all_results)
        results = search_bing_news(query, remaining)
        if results:
            print(f"Found {len(results)} results from Bing News")
            all_results.extend(results)
    
    # If we still don't have enough, try DuckDuckGo
    if len(all_results) < max_articles:
        remaining = max_articles - len(all_results)
        results = search_duckduckgo_news(query, remaining)
        if results:
            print(f"Found {len(results)} results from DuckDuckGo")
            all_results.extend(results)
    
    # If still not enough, try some specific news sites directly
    if len(all_results) < max_articles:
        news_sites = [
            "https://news.yahoo.com",
            "https://www.reuters.com",
            "https://www.bbc.com/news"
        ]
        
        for site in news_sites:
            if len(all_results) >= max_articles:
                break
                
            remaining = max_articles - len(all_results)
            results = search_raw_html(site, query, remaining)
            if results:
                print(f"Found {len(results)} results from {site}")
                all_results.extend(results)
    
    # Deduplicate by URL
    unique_results = []
    seen_urls = set()
    
    for result in all_results:
        if result["url"] not in seen_urls:
            seen_urls.add(result["url"])
            unique_results.append(result)
    
    return unique_results[:max_articles]

# Scrape individual news article
def scrape_news_article(url: str) -> Dict:
    print(f"Scraping article: {url}")
    headers = get_random_headers()
    
    try:
        # First try with WebBaseLoader
        loader = WebBaseLoader(
            web_paths=[url],
            requests_kwargs={"headers": headers}
        )
        document = loader.load()[0]
        text = document.page_content.strip()
        metadata = document.metadata
        
        # If text is too short, try with direct requests + BeautifulSoup
        if len(text) < 50:
            print("Content too short, trying direct parsing...")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script, style elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
                
            # Get title
            title = soup.title.text.strip() if soup.title else "Untitled"
            
            # Extract main content
            article_text = ""
            
            # Try common article content selectors
            selectors = [
                'article', '.article', '.content', '.story', 'main', 
                '.post-content', '.entry-content', '#content'
            ]
            
            for selector in selectors:
                content = soup.select_one(selector)
                if content:
                    paragraphs = content.find_all('p')
                    article_text = '\n\n'.join([p.text.strip() for p in paragraphs])
                    if len(article_text) > 500:  # Only use if substantial content found
                        break
                        
            # If still no good content, just use all paragraphs
            if len(article_text) < 500:
                paragraphs = soup.find_all('p')
                article_text = '\n\n'.join([p.text.strip() for p in paragraphs])
                
            # Look for publish date
            date = None
            date_selectors = ['time', '.date', '.published', 'meta[property="article:published_time"]']
            for selector in date_selectors:
                date_element = soup.select_one(selector)
                if date_element:
                    if date_element.name == 'meta':
                        date = date_element.get('content', '')
                    else:
                        date = date_element.text.strip()
                    break
                    
            return {
                "title": title,
                "text": article_text,
                "snippet": article_text + "..." if len(article_text) > 200 else article_text,
                "publish_date": date or "Unknown",
                "source": url.split('/')[2],
                "url": url
            }
        
        return {
            "title": metadata.get("title", "Untitled"),
            "text": text,
            "snippet": text + "..." if len(text) > 200 else text,
            "publish_date": metadata.get("publish_date", "Unknown"),
            "source": url.split('/')[2],
            "url": url
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

# Summarize article
def summarize_article(article_data: Dict, topic: str) -> str:
    if not article_data or not article_data.get("text") or len(article_data["text"].strip()) < 100:
        return None
    
    # Limit article text length to prevent token limits
    article_text = article_data["text"]
    if len(article_text) > 15000:
        article_text = article_text[:15000] + "..."

    template = """
    Create an SEO-optimized news summary:

    ARTICLE CONTENT: {article_text}
    TITLE: {article_title}
    PUBLISHED: {publish_date}
    URL: {article_url}
    TOPIC: {topic}

    REQUIREMENTS:
    - Title: Custom, SEO-optimized
    - Length: 300-500 words
    - Structure: Lead paragraph, context, key facts
    - Keywords: [KEYWORDS: relevant, keywords]

    OUTPUT:
    ## [Title]

    [Summary]

    **Source:** [Source Name] ([article_url])

    [KEYWORDS: keyword1, keyword2]
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()

    try:
        return chain.invoke({
            "article_text": article_text,
            "article_title": article_data["title"],
            "publish_date": article_data["publish_date"],
            "article_url": article_data["url"],
            "topic": topic
        })
    except Exception as e:
        print(f"Error summarizing article: {e}")
        return None

def main():
    print("Enhanced News Agent Initialized")
    print("==============================")
    print("Using multiple news sources and improved scraping")

    while True:
        query = input("\nEnter a topic to search for news (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        try:
            max_articles = int(input("How many articles do you want to extract and summarize? "))
        except ValueError:
            print("Invalid input, using default of 3 articles.")
            max_articles = 3

        print("\n" + "=" * 50)
        search_results = multi_source_news_search(query, max_articles)

        if not search_results:
            print("No articles found. Try another search query.")
            continue

        for i, result in enumerate(search_results, 1):
            print(f"\n--- ARTICLE {i} ---")
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Source: {result.get('source', 'Unknown')}")
            
            # Add a small delay between requests to avoid rate limiting
            if i > 1:
                time.sleep(2)
                
            scraped_data = scrape_news_article(result['url'])

            if scraped_data and scraped_data.get("text"):
                print("\n=========================== SCRAPED DATA ===========================")
                print(f"Title: {scraped_data['title']}")
                print(f"Source: {scraped_data['source']}")
                print(f"Published: {scraped_data['publish_date']}")
                print(f"Content Preview: {scraped_data['snippet']}")

                summary = summarize_article(scraped_data, query)
                if summary:
                    print("\n=========================== SUMMARY ===========================")
                    print(summary)
                else:
                    print("\nCould not generate summary, text may be too short or inadequate.")
            else:
                print("\nCould not scrape article content.")
            print("=" * 50)

if __name__ == "__main__":
    # Install required packages if missing
    try:
        import requests
        from bs4 import BeautifulSoup
        from langchain_community.document_loaders import WebBaseLoader
    except ImportError:
        print("Installing required packages...")
        os.system("pip install requests beautifulsoup4 langchain-groq langchain-community")
    
    main()













# import os
# import re
# import inspect
# from typing import Dict, List
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_groq import ChatGroq
# from langchain_community.document_loaders import WebBaseLoader
# from phi.agent import Agent
# from phi.tools.googlesearch import GoogleSearch

# # Monkey-patch phi.utils.get_method_sig for Python 3.11+ compatibility
# def patch_phi_utils():
#     try:
#         from phi import utils
#         original_get_method_sig = utils.get_method_sig
        
#         def patched_get_method_sig(method):
#             try:
#                 argspec = inspect.getfullargspec(method)
#             except AttributeError:
#                 sig = inspect.signature(method)
#                 argspec = inspect.FullArgSpec(
#                     args=[p for p in sig.parameters],
#                     varargs=None,
#                     varkw=None,
#                     defaults=None,
#                     kwonlyargs=[],
#                     kwonlydefaults={},
#                     annotations={}
#                 )
#             return {
#                 "args": argspec.args,
#                 "varargs": argspec.varargs,
#                 "keywords": argspec.varkw,
#                 "defaults": argspec.defaults,
#             }
        
#         utils.get_method_sig = patched_get_method_sig
#     except ImportError as e:
#         print(f"Error patching phi.utils: {e}")
#         raise

# # Apply the patch
# patch_phi_utils()

# # Set environment variables
# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
# os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
# os.environ["GOOGLE_CSE_ID"] = os.getenv("GOOGLE_CSE_ID")

# # Validate environment variables
# if not os.getenv("GROQ_API_KEY"):
#     raise ValueError("GROQ_API_KEY not set. Run: set GROQ_API_KEY=your_groq_api_key")
# if not os.getenv("GOOGLE_API_KEY") or not os.getenv("GOOGLE_CSE_ID"):
#     raise ValueError("GOOGLE_API_KEY and GOOGLE_CSE_ID must be set. Run: set GOOGLE_API_KEY=your_key && set GOOGLE_CSE_ID=your_id")

# # Initialize LLM (Groq model)
# llm = ChatGroq(
#     model="meta-llama/llama-4-scout-17b-16e-instruct",
#     api_key=os.getenv("GROQ_API_KEY")
# )

# # Initialize Agent
# try:
#     agent = Agent(
#         tools=[GoogleSearch()],
#         description="You are a news agent that helps users find the latest news.",
#         instructions=[
#             "Given a topic by the user, respond with 4 latest news items about that topic.",
#             "Search for 10 news items and select the top 4 unique items.",
#             "Search in English and in French.",
#         ],
#         show_tool_calls=True,
#         debug_mode=True,
#     )
# except Exception as e:
#     print(f"Error initializing agent: {e}")
#     raise

# # Agent-based news search
# def agent_news_search(query: str, max_articles: int = 4) -> List[Dict]:
#     query_with_context = f"{query} latest news"
#     print(f"Searching with Agent for: {query_with_context}")
    
#     try:
#         response = agent.get_response(query_with_context)
#         articles = []
#         current_article = {}
#         for line in response.split("\n"):
#             if line.startswith("## "):
#                 if current_article:
#                     articles.append(current_article)
#                 current_article = {"title": line[3:].strip()}
#             elif line.startswith("**Source:**"):
#                 match = re.search(r"\((https?://.*?)\)", line)
#                 current_article["url"] = match.group(1) if match else ""
#                 current_article["source"] = line.split("(")[0].replace("**Source:**", "").strip()
#             elif line.startswith("**Date:**"):
#                 current_article["date"] = line.replace("**Date:**", "").strip()
#         if current_article:
#             articles.append(current_article)
        
#         print(f"Found {len(articles)} articles")
#         return articles[:max_articles]
#     except Exception as e:
#         print(f"Agent search error: {e}")
#         return []

# # Scrape individual news article page using LangChain Document Loader
# def scrape_news_article(url: str) -> Dict:
#     try:
#         loader = WebBaseLoader(url)
#         document = loader.load()[0]
#         text = document.page_content.strip()
#         metadata = document.metadata

#         return {
#             "title": metadata.get("title", "Untitled"),
#             "text": text,
#             "snippet": text[:200] + "..." if len(text) > 200 else text,
#             "publish_date": metadata.get("publish_date", "Unknown"),
#             "source": url.split('/')[2],
#             "url": url
#         }
#     except Exception as e:
#         print(f"Error scraping {url}: {e}")
#         return None

# # Summarize article
# def summarize_article(article_data: Dict, topic: str) -> str:
#     if not article_data:
#         return None

#     template = """
#     Create an SEO-optimized news summary:

#     ARTICLE CONTENT: {article_text}
#     TITLE: {article_title}
#     PUBLISHED: {publish_date}
#     URL: {article_url}
#     TOPIC: {topic}

#     REQUIREMENTS:
#     - Title: Custom, SEO-optimized
#     - Length: 300-500 words
#     - Structure: Lead paragraph, context, key facts
#     - Keywords: [KEYWORDS: relevant, keywords]

#     OUTPUT:
#     ## [Title]

#     [Summary]

#     **Source:** [Source Name] ([article_url])

#     [KEYWORDS: keyword1, keyword2]
#     """

#     prompt = ChatPromptTemplate.from_template(template)
#     chain = prompt | llm | StrOutputParser()

#     try:
#         return chain.invoke({
#             "article_text": article_data["text"],
#             "article_title": article_data["title"],
#             "publish_date": article_data["publish_date"],
#             "article_url": article_data["url"],
#             "topic": topic
#         })
#     except Exception as e:
#         print(f"Error summarizing article: {e}")
#         return None

# def main():
#     print("News Agent Initialized")
#     print("=====================")

#     while True:
#         query = input("\nEnter a topic to search for news (or 'exit' to quit): ")
#         if query.lower() == 'exit':
#             break

#         try:
#             max_articles = int(input("How many articles do you want to extract and summarize? (default 4): "))
#         except ValueError:
#             print("Invalid input, using default of 4 articles.")
#             max_articles = 4

#         print("\n" + "=" * 50)
#         search_results = agent_news_search(query, max_articles)

#         if not search_results:
#             print("No news articles found.")
#             print("=" * 50)
#             continue

#         for i, result in enumerate(search_results, 1):
#             print(f"\n--- ARTICLE {i} ---")
#             print(f"Title: {result['title']}")
#             print(f"URL: {result['url']}")
#             print(f"Source: {result.get('source', 'Unknown')}")
#             print(f"Date: {result.get('date', 'Unknown')}")

#             scraped_data = scrape_news_article(result['url'])

#             if scraped_data:
#                 print("\n=========================== SCRAPED DATA ===========================")
#                 print(f"Title: {scraped_data['title']}")
#                 print(f"Source: {scraped_data['source']}")
#                 print(f"Published: {scraped_data['publish_date']}")
#                 print(f"Content Preview: {scraped_data['snippet']}")

#                 summary = summarize_article(scraped_data, query)
#                 if summary:
#                     print("\n=========================== SUMMARY ===========================")
#                     print(summary)
#             print("=" * 50)

# if __name__ == "__main__":
#     # Install required packages if missing
#     try:
#         from phi.agent import Agent
#         from phi.tools.googlesearch import GoogleSearch
#     except ImportError:
#         print("Installing required packages...")
#         os.system("pip install phidata phi langchain-groq langchain-community")
    
#     main()














# # meta-llama/llama-4-scout-17b-16e-instruct
# from dotenv import load_dotenv
# load_dotenv()

# import os
# import requests
# from typing import Dict, List
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_groq import ChatGroq

# # Initialize Groq LLM
# llm = ChatGroq(
#     model="meta-llama/llama-4-scout-17b-16e-instruct",  # or "llama3-70b-8192"
#     api_key=os.getenv("GROQ_API_KEY")
# )

# if not os.getenv("GROQ_API_KEY"):
#     raise ValueError("GROQ_API_KEY not set. Set it with: export GROQ_API_KEY=your_groq_api_key")

# # Get Firecrawl API key
# FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
# if not FIRECRAWL_API_KEY:
#     raise ValueError("FIRECRAWL_API_KEY not set. Set it with: export FIRECRAWL_API_KEY=your_api_key")

# def scrape_website(url: str) -> Dict:
#     """Scrape a website using the Firecrawl API directly"""
#     api_url = "https://api.firecrawl.dev/v1/scrape"
    
#     payload = {
#         "url": url,
#         "formats": ["markdown"],
#         "onlyMainContent": True,
#         "blockAds": True
#     }
    
#     headers = {
#         "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
#         "Content-Type": "application/json"
#     }
    
#     try:
#         response = requests.post(api_url, json=payload, headers=headers)
#         response.raise_for_status()  # Raise exception for 4xx/5xx responses
#         return response.json()
#     except Exception as e:
#         print(f"Error scraping {url}: {e}")
#         return None

# def firecrawl_search(query: str, max_articles: int = 3) -> List[Dict]:
#     """Search for news articles using Firecrawl API directly"""
#     print(f"Searching for: {query} latest news")
    
#     # First, scrape Google News search results
#     search_url = f"https://news.google.com/search?q={query}"
#     print(f"Attempting to scrape search page: {search_url}")
    
#     search_results = scrape_website(search_url)
    
#     if not search_results:
#         print("Failed to get search results")
#         return []
    
#     # Extract links from the markdown content
#     # This is a simplified approach - in production you'd want more robust parsing
#     content = search_results.get("markdown", "")
#     articles = []
    
#     # Try to extract URLs directly from the Google News results
#     import re
#     urls = re.findall(r'https?://[^\s\)\]\"\']+', content)
#     news_urls = [url for url in urls if 'google.com' not in url]
    
#     print(f"Found {len(news_urls)} potential news URLs")
    
#     # Scrape each news URL
#     for i, url in enumerate(news_urls[:max_articles]):
#         print(f"Scraping article {i+1}: {url}")
#         article_data = scrape_website(url)
        
#         if article_data:
#             articles.append({
#                 "title": article_data.get("title", f"News about {query}"),
#                 "url": url,
#                 "source": url.split('/')[2] if '//' in url else "Unknown",
#                 "text": article_data.get("markdown", "")
#             })
    
#     # If we couldn't extract any articles, return the search page itself
#     if not articles:
#         print("Could not extract individual articles, using search page content")
#         articles = [{
#             "title": search_results.get("title", f"News about {query}"),
#             "url": search_url,
#             "source": "Google News",
#             "text": content
#         }]
        
#     return articles[:max_articles]

# def summarize_article(article_data: Dict, topic: str) -> str:
#     """Summarize article using Groq"""
#     if not article_data or not article_data.get("text"):
#         return None

#     template = """Create a concise news summary:
#     ARTICLE: {article_text}
    
#     Requirements:
#     - 3-5 bullet points of key facts
#     - Include important names/dates
#     - Keep under 200 words
    
#     Summary:"""
    
#     prompt = ChatPromptTemplate.from_template(template)
#     chain = prompt | llm | StrOutputParser()
    
#     try:
#         # Limit text length to avoid token limits
#         article_text = article_data["text"][:10000]  # Truncate to 10K chars
#         return chain.invoke({
#             "article_text": article_text,
#             "topic": topic
#         })
#     except Exception as e:
#         print(f"Error summarizing: {e}")
#         return None

# def main():
#     print("News Agent with Groq+Firecrawl")
#     print("==============================")
    
#     while True:
#         query = input("\nEnter news topic (or 'exit'): ").strip()
#         if query.lower() == 'exit':
#             break
        
#         articles = firecrawl_search(query)
        
#         if not articles:
#             print("No articles found. Try another search query.")
#             continue
            
#         for i, article in enumerate(articles, 1):
#             print(f"\n--- Article {i} ---")
#             print(f"Title: {article['title']}")
#             print(f"Source: {article['source']}")
#             print(f"URL: {article['url']}")
            
#             if article.get("text"):
#                 summary = summarize_article(article, query)
#                 if summary:
#                     print("\n=== Summary ===")
#                     print(summary)
#             else:
#                 print("\nNo content available to summarize.")
#             print("=" * 50)

# if __name__ == "__main__":
#     # Install required packages
#     try:
#         import requests
#     except ImportError:
#         print("Installing required packages...")
#         os.system("pip install requests langchain-groq")
    
#     main()