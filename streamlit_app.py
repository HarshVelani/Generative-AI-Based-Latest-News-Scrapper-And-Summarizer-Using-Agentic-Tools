# import os
# import re
# import streamlit as st
# from typing import Dict, List
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_groq import ChatGroq
# from langchain_community.tools import DuckDuckGoSearchResults
# from langchain_community.document_loaders import WebBaseLoader

# # Set page configuration
# st.set_page_config(
#     page_title="News Summarizer",
#     page_icon="📰",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Initialize session state for storing API key
# if "groq_api_key" not in st.session_state:
#     st.session_state.groq_api_key = ""
# if "search_history" not in st.session_state:
#     st.session_state.search_history = []
# if "summarized_articles" not in st.session_state:
#     st.session_state.summarized_articles = []

# # Sidebar for API key input
# with st.sidebar:
#     st.title("📰 News Summarizer")
#     st.markdown("---")
    
#     # API key input
#     api_key = st.text_input("Enter Groq API Key:", 
#                            value=st.session_state.groq_api_key,
#                            type="password", 
#                            help="Your Groq API key is required to use the LLM for summarization")
    
#     if api_key:
#         st.session_state.groq_api_key = api_key
    
#     st.markdown("---")
#     st.markdown("### Search History")
    
#     # Display search history
#     if st.session_state.search_history:
#         for i, query in enumerate(st.session_state.search_history):
#             st.markdown(f"- {query}")
#     else:
#         st.markdown("No searches yet")

# # Function to initialize LLM with API key
# def initialize_llm(api_key: str):
#     try:
#         llm = ChatGroq(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             api_key=api_key
#         )
#         return llm
#     except Exception as e:
#         st.error(f"Error initializing LLM: {e}")
#         return None

# # DuckDuckGo news search function
# def langchain_duckduckgo_search(query: str, max_articles: int = 1) -> List[Dict]:
#     search = DuckDuckGoSearchResults(backend="news", max_results=max_articles * 2)  # Request extra in case some fail
#     query_with_context = f"{query} latest news"
    
#     with st.spinner(f"Searching for latest news on '{query}'..."):
#         try:
#             results = search.invoke(query_with_context)
            
#             text = results
#             pattern = re.compile(
#                 r"snippet:\s*(.*?),\s*title:\s*(.*?),\s*link:\s*(.*?),\s*date:\s*(.*?),\s*source:\s*(.*?)(?:,|$)",
#                 re.DOTALL
#             )

#             matches = pattern.findall(text)

#             articles = []
#             for match in matches:
#                 article = {
#                     "title": match[1].strip(),
#                     "url": match[2].strip(),
#                     "date": match[3].strip() if len(match) > 3 else "Unknown",
#                     "source": match[4].strip() if len(match) > 4 else "Unknown"
#                 }
#                 articles.append(article)

#             return articles[:max_articles]

#         except Exception as e:
#             st.error(f"DuckDuckGo search error: {e}")
#             return []

# # Scrape individual news article page
# def scrape_news_article(url: str) -> Dict:
#     try:
#         with st.spinner(f"Scraping article from {url}..."):
#             loader = WebBaseLoader(url)
#             document = loader.load()[0]
#             text = document.page_content.strip()
#             metadata = document.metadata

#             return {
#                 "title": metadata.get("title", "Untitled"),
#                 "text": text,
#                 "snippet": text[:500] + "..." if len(text) > 500 else text,
#                 "publish_date": metadata.get("publish_date", "Unknown"),
#                 "source": url.split('/')[2],
#                 "url": url
#             }
#     except Exception as e:
#         st.error(f"Error scraping {url}: {e}")
#         return None

# # Summarize article
# def summarize_article(llm, article_data: Dict, topic: str) -> str:
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
#         with st.spinner("Generating article summary..."):
#             return chain.invoke({
#                 "article_text": article_data["text"],
#                 "article_title": article_data["title"],
#                 "publish_date": article_data["publish_date"],
#                 "article_url": article_data["url"],
#                 "topic": topic
#             })
#     except Exception as e:
#         st.error(f"Error summarizing article: {e}")
#         return None

# # Main application
# def main():
#     # Main content
#     st.title("🔍 AI News Summarizer")
#     st.markdown("""
#     This application searches for the latest news articles on your chosen topic,
#     extracts the content, and generates concise, SEO-optimized summaries.
#     """)
    
#     # API key validation
#     if not st.session_state.groq_api_key:
#         st.warning("⚠️ Please enter your Groq API key in the sidebar to continue.")
#         st.stop()
    
#     # Initialize LLM
#     llm = initialize_llm(st.session_state.groq_api_key)
#     if not llm:
#         st.stop()
    
#     # Search form
#     with st.form("search_form"):
#         col1, col2 = st.columns([3, 1])
        
#         with col1:
#             search_query = st.text_input("Enter a topic or person to search:", 
#                                          placeholder="e.g., AI, Climate Change, Elon Musk")
        
#         with col2:
#             num_articles = st.number_input("Number of articles:", 
#                                           min_value=1, max_value=5, value=2)
        
#         submit_button = st.form_submit_button("Search & Summarize")
    
#     # Process search request
#     if submit_button and search_query:
#         # Add to search history
#         if search_query not in st.session_state.search_history:
#             st.session_state.search_history.insert(0, search_query)
#             # Keep only the last 10 searches
#             st.session_state.search_history = st.session_state.search_history[:10]
        
#         # Search for articles
#         articles = langchain_duckduckgo_search(search_query, num_articles)
        
#         if not articles:
#             st.error("No articles found for this query. Try a different search term.")
#             st.stop()
        
#         st.success(f"Found {len(articles)} articles about '{search_query}'")
        
#         # Process each article
#         summarized_articles = []
        
#         for i, article in enumerate(articles):
#             st.markdown(f"### Processing Article {i+1}: {article['title']}")
            
#             # Display original article info
#             with st.expander("Original Article Details"):
#                 st.markdown(f"**Source:** {article['source']}")
#                 st.markdown(f"**Date:** {article['date']}")
#                 st.markdown(f"**URL:** [{article['url']}]({article['url']})")
            
#             # Scrape and summarize
#             scraped_data = scrape_news_article(article['url'])
            
#             if scraped_data:
#                 with st.expander("Raw Scraped Content"):
#                     st.text_area("Content preview:", scraped_data['snippet'], height=150)
                
#                 summary = summarize_article(llm, scraped_data, search_query)
                
#                 if summary:
#                     summarized_articles.append(summary)
                    
#                     # Display the summary
#                     st.markdown("## Summary")
#                     st.markdown(summary)
#                     st.markdown("---")
#                 else:
#                     st.error("Failed to generate summary for this article.")
#             else:
#                 st.error("Failed to scrape content from this article.")
        
#         # Store the summarized articles
#         if summarized_articles:
#             st.session_state.summarized_articles = summarized_articles
    
#     # Display previously summarized articles if they exist and no new search
#     elif not submit_button and st.session_state.summarized_articles:
#         st.markdown("## Previously Summarized Articles")
        
#         for i, summary in enumerate(st.session_state.summarized_articles):
#             with st.expander(f"Article {i+1}"):
#                 st.markdown(summary)

# if __name__ == "__main__":
#     main()


# import os
# import re
# import time
# import requests
# import streamlit as st
# from typing import Dict, List
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_groq import ChatGroq
# from langchain_community.tools import DuckDuckGoSearchResults
# from langchain_community.document_loaders import WebBaseLoader
# from bs4 import BeautifulSoup
# from urllib3.exceptions import InsecureRequestWarning
# import urllib3

# # Suppress only the single InsecureRequestWarning
# urllib3.disable_warnings(InsecureRequestWarning)

# # Set page configuration
# st.set_page_config(
#     page_title="News Summarizer",
#     page_icon="📰",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Initialize session state for storing API key
# if "groq_api_key" not in st.session_state:
#     st.session_state.groq_api_key = ""
# if "search_history" not in st.session_state:
#     st.session_state.search_history = []
# if "summarized_articles" not in st.session_state:
#     st.session_state.summarized_articles = []

# # Sidebar for API key input
# with st.sidebar:
#     st.title("📰 News Summarizer")
#     st.markdown("---")
    
#     # API key input with unique key
#     api_key = st.text_input("Enter Groq API Key:", 
#                            value=st.session_state.groq_api_key,
#                            type="password", 
#                            help="Your Groq API key is required to use the LLM for summarization",
#                            key="api_key_input")
    
#     if api_key:
#         st.session_state.groq_api_key = api_key
    
#     st.markdown("---")
#     st.markdown("### Search History")
    
#     # Display search history
#     if st.session_state.search_history:
#         for i, query in enumerate(st.session_state.search_history):
#             st.markdown(f"- {query}")
#     else:
#         st.markdown("No searches yet")

# # Function to initialize LLM with API key
# def initialize_llm(api_key: str):
#     try:
#         llm = ChatGroq(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             api_key=api_key
#         )
#         return llm
#     except Exception as e:
#         st.error(f"Error initializing LLM: {e}")
#         return None

# # DuckDuckGo news search function
# def langchain_duckduckgo_search(query: str, max_articles: int = 1) -> List[Dict]:
#     search = DuckDuckGoSearchResults(backend="news", max_results=max_articles * 3)  # Request extra in case some fail
#     query_with_context = f"{query} latest news"
    
#     with st.spinner(f"Searching for latest news on '{query}'..."):
#         try:
#             results = search.invoke(query_with_context)
            
#             text = results
#             pattern = re.compile(
#                 r"snippet:\s*(.*?),\s*title:\s*(.*?),\s*link:\s*(.*?),\s*date:\s*(.*?),\s*source:\s*(.*?)(?:,|$)",
#                 re.DOTALL
#             )

#             matches = pattern.findall(text)

#             articles = []
#             for match in matches:
#                 article = {
#                     "title": match[1].strip(),
#                     "url": match[2].strip(),
#                     "date": match[3].strip() if len(match) > 3 else "Unknown",
#                     "source": match[4].strip() if len(match) > 4 else "Unknown"
#                 }
#                 articles.append(article)

#             return articles[:max_articles]

#         except Exception as e:
#             st.error(f"DuckDuckGo search error: {e}")
#             return []

# # Fallback scraper using requests and BeautifulSoup
# def fallback_scraper(url: str) -> Dict:
#     try:
#         # Add user-agent to avoid blocking
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }
        
#         # Use verify=False for SSL issues, but with warning
#         response = requests.get(url, headers=headers, timeout=10, verify=False)
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # Try to extract title
#         title = soup.title.text if soup.title else "Untitled"
        
#         # Extract text from paragraphs
#         paragraphs = soup.find_all('p')
#         text = '\n\n'.join([p.get_text().strip() for p in paragraphs])
        
#         # Get domain as source
#         source = url.split('/')[2]
        
#         return {
#             "title": title,
#             "text": text,
#             "snippet": text[:500] + "..." if len(text) > 500 else text,
#             "publish_date": "Unknown",
#             "source": source,
#             "url": url
#         }
#     except Exception as e:
#         st.warning(f"Fallback scraper also failed: {e}")
#         return None

# # Scrape individual news article page with retry and fallback
# def scrape_news_article(url: str) -> Dict:
#     progress_bar = st.progress(0)
#     status_text = st.empty()
    
#     try:
#         status_text.text(f"Attempting to scrape article from {url}...")
#         progress_bar.progress(10)
        
#         # First try: WebBaseLoader (LangChain)
#         try:
#             status_text.text("Using primary scraper...")
#             progress_bar.progress(30)
#             loader = WebBaseLoader(url)
#             document = loader.load()[0]
#             text = document.page_content.strip()
#             metadata = document.metadata
            
#             progress_bar.progress(70)
#             result = {
#                 "title": metadata.get("title", "Untitled"),
#                 "text": text,
#                 "snippet": text[:500] + "..." if len(text) > 500 else text,
#                 "publish_date": metadata.get("publish_date", "Unknown"),
#                 "source": url.split('/')[2],
#                 "url": url
#             }
#             progress_bar.progress(100)
#             status_text.text("Successfully scraped article!")
#             time.sleep(0.5)  # Let user see success message
#             status_text.empty()
#             progress_bar.empty()
#             return result
            
#         except Exception as e:
#             # Second try: Fallback to requests + BeautifulSoup
#             st.warning(f"Primary scraper failed: {e}")
#             status_text.text("Trying fallback scraper...")
#             progress_bar.progress(50)
            
#             result = fallback_scraper(url)
#             if result:
#                 progress_bar.progress(100)
#                 status_text.text("Successfully scraped article with fallback method!")
#                 time.sleep(0.5)
#                 status_text.empty()
#                 progress_bar.empty()
#                 return result
#             else:
#                 raise Exception("All scraping methods failed")
                
#     except Exception as e:
#         progress_bar.empty()
#         status_text.empty()
#         st.error(f"Error scraping {url}: {e}")
        
#         # Return minimal info if everything fails
#         return {
#             "title": "Could not extract title",
#             "text": f"Failed to extract content from this article at {url}. The website may be blocking scrapers or have unusual formatting.",
#             "snippet": "Content extraction failed.",
#             "publish_date": "Unknown",
#             "source": url.split('/')[2],
#             "url": url
#         }

# # Summarize article
# def summarize_article(llm, article_data: Dict, topic: str) -> str:
#     if not article_data or article_data["text"].startswith("Failed to extract"):
#         return f"""
# ## Could Not Generate Summary

# Unfortunately, we couldn't generate a summary for this article because the content could not be extracted properly. 
# The website may be blocking content scrapers or using technical measures that prevent automatic extraction.

# **Source:** [{article_data["source"]}]({article_data["url"]})

# [KEYWORDS: {topic}, news]
# """

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
#     - If the content seems incomplete or unclear, mention this in your summary

#     OUTPUT:
#     ## [Title]

#     [Summary]

#     **Source:** [Source Name] ([article_url])

#     **Published on:** Published date

#     [KEYWORDS: keyword1, keyword2]
#     """

#     prompt = ChatPromptTemplate.from_template(template)
#     chain = prompt | llm | StrOutputParser()

#     try:
#         with st.spinner("Generating article summary..."):
#             result = chain.invoke({
#                 "article_text": article_data["text"],
#                 "article_title": article_data["title"],
#                 "publish_date": article_data["publish_date"],
#                 "article_url": article_data["url"],
#                 "topic": topic
#             })
#             return result
#     except Exception as e:
#         st.error(f"Error summarizing article: {e}")
#         return f"""
# ## Summary Generation Failed

# We encountered an error while trying to summarize this article: {str(e)}

# **Source:** [{article_data["source"]}]({article_data["url"]})

# [KEYWORDS: {topic}, error]
# """

# # Test API key function
# def test_api_key(api_key: str) -> bool:
#     try:
#         llm = ChatGroq(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             api_key=api_key
#         )
#         # Simple test query
#         prompt = ChatPromptTemplate.from_template("Say 'API key is valid'")
#         chain = prompt | llm | StrOutputParser()
#         result = chain.invoke({})
#         return "valid" in result.lower()
#     except Exception as e:
#         st.error(f"API key test failed: {e}")
#         return False

# # Main application
# def main():
#     # Main content
#     st.title("🔍 AI News Summarizer")
#     st.markdown("""
#     This application searches for the latest news articles on your chosen topic,
#     extracts the content, and generates concise, SEO-optimized summaries.
#     """)
    
#     # API key validation
#     if not st.session_state.groq_api_key:
#         st.warning("⚠️ Please enter your Groq API key in the sidebar to continue.")
#         st.stop()
    
#     # Test API key if requested
#     col1, col2 = st.columns([3, 1])
#     with col2:
#         if st.button("Test API Key", key="test_api"):
#             with st.spinner("Testing API key..."):
#                 if test_api_key(st.session_state.groq_api_key):
#                     st.success("✅ API key is valid!")
#                 else:
#                     st.error("❌ API key is invalid or there was an error.")
    
#     # Initialize LLM
#     llm = initialize_llm(st.session_state.groq_api_key)
#     if not llm:
#         st.stop()
    
#     # Search form
#     with st.form("search_form"):
#         col1, col2 = st.columns([3, 1])
        
#         with col1:
#             search_query = st.text_input("Enter a topic or person to search:", 
#                                          placeholder="e.g., AI, Climate Change, Elon Musk",
#                                          key="search_query_input")
        
#         with col2:
#             num_articles = st.number_input("Number of articles:", 
#                                           min_value=1, max_value=4, value=2,
#                                           key="num_articles_input")
        
#         submit_button = st.form_submit_button("Search & Summarize")
    
#     # Process search request
#     if submit_button and search_query:
#         # Add to search history
#         if search_query not in st.session_state.search_history:
#             st.session_state.search_history.insert(0, search_query)
#             # Keep only the last 10 searches
#             st.session_state.search_history = st.session_state.search_history[:10]
        
#         # Search for articles
#         articles = langchain_duckduckgo_search(search_query, num_articles)
        
#         if not articles:
#             st.error("No articles found for this query. Try a different search term.")
#             st.stop()
        
#         st.success(f"Found {len(articles)} articles about '{search_query}'")
        
#         # Process each article
#         summarized_articles = []
        
#         for i, article in enumerate(articles):
#             st.markdown(f"### Processing Article {i+1}: {article['title']}")
            
#             # Display original article info
#             with st.expander("Original Article Details", expanded=False):
#                 st.markdown(f"**Source:** {article['source']}")
#                 st.markdown(f"**Date:** {article['date']}")
#                 st.markdown(f"**URL:** [{article['url']}]({article['url']})")
            
#             # Scrape and summarize
#             scraped_data = scrape_news_article(article['url'])
            
#             if scraped_data:
#                 with st.expander("Raw Scraped Content", expanded=False):
#                     # Add unique key for each text_area
#                     st.text_area(
#                         "Content preview:", 
#                         scraped_data['snippet'], 
#                         height=150,
#                         key=f"article_preview_{i}"
#                     )
                
#                 summary = summarize_article(llm, scraped_data, search_query)
                
#                 if summary:
#                     summarized_articles.append(summary)
                    
#                     # Display the summary
#                     summary_container = st.container()
#                     with summary_container:
#                         st.markdown("## Summary")
#                         st.markdown(summary)
#                         st.markdown("---")
#                 else:
#                     st.error("Failed to generate summary for this article.")
#             else:
#                 st.error("Failed to scrape content from this article.")
        
#         # Store the summarized articles
#         if summarized_articles:
#             st.session_state.summarized_articles = summarized_articles
    
#     # Display previously summarized articles if they exist and no new search
#     elif not submit_button and st.session_state.summarized_articles:
#         st.markdown("## Previously Summarized Articles")
        
#         for i, summary in enumerate(st.session_state.summarized_articles):
#             with st.expander(f"Article {i+1}", expanded=False):
#                 st.markdown(summary)

# if __name__ == "__main__":
#     main()











# new api, bing news search and duckduckgo search   1

# import streamlit as st
# import os
# import re
# import requests
# import time
# import random
# from typing import Dict, List
# from bs4 import BeautifulSoup
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_groq import ChatGroq
# from langchain_community.document_loaders import WebBaseLoader

# st.set_page_config(
#     page_title="News Scraper & Summarizer",
#     page_icon="📰",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Session state initialization
# if 'search_results' not in st.session_state:
#     st.session_state.search_results = []
# if 'api_keys_valid' not in st.session_state:
#     st.session_state.api_keys_valid = False
# if 'llm' not in st.session_state:
#     st.session_state.llm = None

# # Define user agents to rotate
# USER_AGENTS = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
#     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# ]

# # Function definitions
# def get_random_headers():
#     """Get random headers to avoid detection"""
#     return {
#         'User-Agent': random.choice(USER_AGENTS),
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.5',
#         'Referer': 'https://www.google.com/',
#         'DNT': '1',
#         'Connection': 'keep-alive',
#         'Upgrade-Insecure-Requests': '1',
#         'Sec-Fetch-Dest': 'document',
#         'Sec-Fetch-Mode': 'navigate',
#         'Sec-Fetch-Site': 'none',
#         'Sec-Fetch-User': '?1',
#         'Cache-Control': 'max-age=0'
#     }

# def search_duckduckgo_news(query: str, max_results: int = 3):
#     """Search news using DuckDuckGo"""
#     search_url = f"https://duckduckgo.com/html/?q={query}+news"
#     headers = get_random_headers()
   
#     try:
#         with st.spinner(f"Searching DuckDuckGo for: {query}"):
#             response = requests.get(search_url, headers=headers)
#             response.raise_for_status()
           
#             soup = BeautifulSoup(response.text, 'html.parser')
#             results = []
           
#             # Extract links from search results
#             for result in soup.select('.result__a'):
#                 link = result.get('href')
#                 if link:
#                     # Clean up URL
#                     if '/l/?uddg=' in link:
#                         # Extract the actual URL from DuckDuckGo's redirect
#                         decoded_url = link.split('/l/?uddg=')[1].split('&')[0]
#                         link = requests.utils.unquote(decoded_url)
                   
#                     results.append({
#                         "title": result.text.strip(),
#                         "url": link,
#                         "source": link.split('/')[2] if '//' in link else "Unknown source",
#                         "snippet": ""
#                     })
                   
#                     if len(results) >= max_results:
#                         break
                       
#             return results
#     except Exception as e:
#         st.error(f"DuckDuckGo search error: {e}")
#         return []

# def search_bing_news(query: str, max_results: int = 3):
#     """Search news using Bing"""
#     search_url = f"https://www.bing.com/news/search?q={query.replace(' ', '+')}"
#     headers = get_random_headers()
   
#     try:
#         with st.spinner(f"Searching Bing News for: {query}"):
#             response = requests.get(search_url, headers=headers)
#             response.raise_for_status()
           
#             soup = BeautifulSoup(response.text, 'html.parser')
#             results = []
           
#             # Extract news articles
#             for article in soup.select('.news-card'):
#                 link_element = article.select_one('a.title')
#                 if link_element:
#                     link = link_element.get('href')
#                     title = link_element.text.strip()
                   
#                     source_element = article.select_one('.source')
#                     source = source_element.text.strip() if source_element else "Unknown"
                   
#                     snippet_element = article.select_one('.snippet')
#                     snippet = snippet_element.text.strip() if snippet_element else ""
                   
#                     if link and link.startswith('http'):
#                         results.append({
#                             "title": title,
#                             "url": link,
#                             "source": source,
#                             "snippet": snippet
#                         })
                       
#                         if len(results) >= max_results:
#                             break
           
#             return results
#     except Exception as e:
#         st.error(f"Bing News search error: {e}")
#         return []

# def news_api_search(query: str, max_results: int = 3, api_key: str = None):
#     """Search using NewsAPI if API key is available"""
#     if not api_key:
#         st.warning("NEWS_API_KEY not provided, skipping NewsAPI search")
#         return []
       
#     url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={api_key}"
   
#     try:
#         with st.spinner(f"Searching NewsAPI for: {query}"):
#             response = requests.get(url)
#             response.raise_for_status()
#             data = response.json()
           
#             results = []
#             if data["status"] == "ok" and data["totalResults"] > 0:
#                 for article in data["articles"][:max_results]:
#                     results.append({
#                         "title": article["title"],
#                         "url": article["url"],
#                         "source": article["source"]["name"],
#                         "snippet": article["description"]
#                     })
#             return results
#     except Exception as e:
#         st.error(f"NewsAPI search error: {e}")
#         return []

# def search_raw_html(url: str, query: str, max_results: int = 3):
#     """Extract links from raw HTML of a news site"""
#     headers = get_random_headers()
   
#     try:
#         with st.spinner(f"Searching {url} for: {query}"):
#             response = requests.get(url, headers=headers)
#             response.raise_for_status()
           
#             # Find all links
#             soup = BeautifulSoup(response.text, 'html.parser')
#             results = []
           
#             # Look for links that might contain the query terms
#             query_terms = query.lower().split()
#             links = soup.find_all('a', href=True)
           
#             for link in links:
#                 href = link.get('href')
#                 text = link.text.strip()
               
#                 # Skip empty links, navigation, etc.
#                 if (not href or not text or len(text) < 15 or
#                     href.startswith('#') or 'javascript:' in href):
#                     continue
                   
#                 # Make absolute URL if needed
#                 if href.startswith('/'):
#                     href = f"{url.split('//', 1)[0]}//{url.split('//', 1)[1].split('/', 1)[0]}{href}"
#                 elif not href.startswith(('http://', 'https://')):
#                     continue
                   
#                 # Check if link text contains any query terms
#                 if any(term in text.lower() for term in query_terms):
#                     results.append({
#                         "title": text,
#                         "url": href,
#                         "source": href.split('/')[2] if '//' in href else "Unknown",
#                         "snippet": ""
#                     })
                   
#                     if len(results) >= max_results:
#                         break
                       
#             return results
#     except Exception as e:
#         st.error(f"Raw HTML search error for {url}: {e}")
#         return []

# def multi_source_news_search(query: str, max_articles: int = 3, news_api_key: str = None) -> List[Dict]:
#     """Search multiple news sources and aggregate results"""
#     all_results = []
    
#     progress_bar = st.progress(0)
#     progress_text = st.empty()
    
#     # Try NewsAPI first if available
#     if news_api_key:
#         progress_text.text("Searching NewsAPI...")
#         results = news_api_search(query, max_articles, news_api_key)
#         if results:
#             st.success(f"Found {len(results)} results from NewsAPI")
#             all_results.extend(results)
#         progress_bar.progress(0.25)
   
#     # If we don't have enough results, try Bing News
#     if len(all_results) < max_articles:
#         progress_text.text("Searching Bing News...")
#         remaining = max_articles - len(all_results)
#         results = search_bing_news(query, remaining)
#         if results:
#             st.success(f"Found {len(results)} results from Bing News")
#             all_results.extend(results)
#         progress_bar.progress(0.5)
   
#     # If we still don't have enough, try DuckDuckGo
#     if len(all_results) < max_articles:
#         progress_text.text("Searching DuckDuckGo...")
#         remaining = max_articles - len(all_results)
#         results = search_duckduckgo_news(query, remaining)
#         if results:
#             st.success(f"Found {len(results)} results from DuckDuckGo")
#             all_results.extend(results)
#         progress_bar.progress(0.75)
   
#     # If still not enough, try some specific news sites directly
#     if len(all_results) < max_articles:
#         progress_text.text("Searching direct news sites...")
#         news_sites = [
#             "https://news.yahoo.com",
#             "https://www.reuters.com",
#             "https://www.bbc.com/news"
#         ]
       
#         for site in news_sites:
#             if len(all_results) >= max_articles:
#                 break
               
#             remaining = max_articles - len(all_results)
#             results = search_raw_html(site, query, remaining)
#             if results:
#                 st.success(f"Found {len(results)} results from {site}")
#                 all_results.extend(results)
    
#     progress_bar.progress(1.0)
#     progress_text.empty()
   
#     # Deduplicate by URL
#     unique_results = []
#     seen_urls = set()
   
#     for result in all_results:
#         if result["url"] not in seen_urls:
#             seen_urls.add(result["url"])
#             unique_results.append(result)
   
#     return unique_results[:max_articles]

# # Scrape individual news article
# def scrape_news_article(url: str) -> Dict:
#     with st.spinner(f"Scraping article: {url}"):
#         headers = get_random_headers()
       
#         try:
#             # First try with WebBaseLoader
#             loader = WebBaseLoader(
#                 web_paths=[url],
#                 requests_kwargs={"headers": headers}
#             )
#             document = loader.load()[0]
#             text = document.page_content.strip()
#             metadata = document.metadata
           
#             # If text is too short, try with direct requests + BeautifulSoup
#             if len(text) < 50:
#                 st.info("Content too short, trying direct parsing...")
#                 response = requests.get(url, headers=headers)
#                 response.raise_for_status()
               
#                 soup = BeautifulSoup(response.text, 'html.parser')
               
#                 # Remove script, style elements
#                 for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
#                     element.decompose()
                   
#                 # Get title
#                 title = soup.title.text.strip() if soup.title else "Untitled"
               
#                 # Extract main content
#                 article_text = ""
               
#                 # Try common article content selectors
#                 selectors = [
#                     'article', '.article', '.content', '.story', 'main',
#                     '.post-content', '.entry-content', '#content'
#                 ]
               
#                 for selector in selectors:
#                     content = soup.select_one(selector)
#                     if content:
#                         paragraphs = content.find_all('p')
#                         article_text = '\n\n'.join([p.text.strip() for p in paragraphs])
#                         if len(article_text) > 500:  # Only use if substantial content found
#                             break
                           
#                 # If still no good content, just use all paragraphs
#                 if len(article_text) < 500:
#                     paragraphs = soup.find_all('p')
#                     article_text = '\n\n'.join([p.text.strip() for p in paragraphs])
                   
#                 # Look for publish date
#                 date = None
#                 date_selectors = ['time', '.date', '.published', 'meta[property="article:published_time"]']
#                 for selector in date_selectors:
#                     date_element = soup.select_one(selector)
#                     if date_element:
#                         if date_element.name == 'meta':
#                             date = date_element.get('content', '')
#                         else:
#                             date = date_element.text.strip()
#                         break
                       
#                 return {
#                     "title": title,
#                     "text": article_text,
#                     "snippet": article_text[:200] + "..." if len(article_text) > 200 else article_text,
#                     "publish_date": date or "Unknown",
#                     "source": url.split('/')[2],
#                     "url": url
#                 }
           
#             return {
#                 "title": metadata.get("title", "Untitled"),
#                 "text": text,
#                 "snippet": text[:200] + "..." if len(text) > 200 else text,
#                 "publish_date": metadata.get("publish_date", "Unknown"),
#                 "source": url.split('/')[2],
#                 "url": url
#             }
#         except Exception as e:
#             st.error(f"Error scraping {url}: {e}")
#             return None

# # Summarize article
# def summarize_article(article_data: Dict, topic: str, llm) -> str:
#     if not article_data or not article_data.get("text") or len(article_data["text"].strip()) < 100:
#         return None
   
#     # Limit article text length to prevent token limits
#     article_text = article_data["text"]
#     if len(article_text) > 15000:
#         article_text = article_text[:15000] + "..."

#     with st.spinner("Generating summary..."):
#         template = """
#         Create an SEO-optimized news summary:
     
#         ARTICLE CONTENT: {article_text}
#         TITLE: {article_title}
#         PUBLISHED: {publish_date}
#         URL: {article_url}
#         TOPIC: {topic}
     
#         REQUIREMENTS:
#         - Title: Custom, SEO-optimized
#         - Length: 300-500 words
#         - Structure: Lead paragraph, context, key facts
#         - Keywords: [KEYWORDS: relevant, keywords]
     
#         OUTPUT:
#         ## [Title]
     
#         [Summary]
     
#         **Source:** [Source Name] ([article_url])
     
#         [KEYWORDS: keyword1, keyword2]
#         """
     
#         prompt = ChatPromptTemplate.from_template(template)
#         chain = prompt | llm | StrOutputParser()
     
#         try:
#             return chain.invoke({
#                 "article_text": article_text,
#                 "article_title": article_data["title"],
#                 "publish_date": article_data["publish_date"],
#                 "article_url": article_data["url"],
#                 "topic": topic
#             })
#         except Exception as e:
#             st.error(f"Error summarizing article: {e}")
#             return None

# def validate_groq_api_key(api_key):
#     """Validate the GROQ API key by making a simple request"""
#     if not api_key:
#         return False
    
#     try:
#         # Just initialize the client to check
#         llm = ChatGroq(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             api_key=api_key
#         )
#         return True
#     except Exception as e:
#         st.error(f"Invalid GROQ API key: {e}")
#         return False

# def validate_news_api_key(api_key):
#     """Validate the NewsAPI key by making a simple request"""
#     if not api_key:
#         # NewsAPI is optional, so we return True if not provided
#         return True
    
#     url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
#     try:
#         response = requests.get(url)
#         data = response.json()
#         if data.get("status") == "ok":
#             return True
#         else:
#             st.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
#             return False
#     except Exception as e:
#         st.error(f"Failed to validate NewsAPI key: {e}")
#         return False

# # Main Streamlit app
# def main():
#     st.title("📰 News Scraper & Summarizer")
    
#     # Sidebar for API keys
#     with st.sidebar:
#         st.header("API Keys")
        
#         # Groq API Key (required)
#         groq_api_key = st.text_input("Groq API Key (required)", 
#                                      value=st.session_state.get('groq_api_key', ''),
#                                      type="password",
#                                      help="Required for summarization. Get one from https://console.groq.com/")
        
#         # News API Key (optional)
#         news_api_key = st.text_input("News API Key (optional)", 
#                                     value=st.session_state.get('news_api_key', ''),
#                                     type="password",
#                                     help="Optional for better news search. Get one from https://newsapi.org/")
        
#         if st.button("Validate API Keys"):
#             with st.spinner("Validating API keys..."):
#                 groq_valid = validate_groq_api_key(groq_api_key)
#                 news_valid = validate_news_api_key(news_api_key)
                
#                 if groq_valid:
#                     st.session_state.groq_api_key = groq_api_key
#                     st.session_state.llm = ChatGroq(
#                         model="meta-llama/llama-4-scout-17b-16e-instruct",
#                         api_key=groq_api_key
#                     )
#                     st.success("✅ Groq API key validated!")
#                 else:
#                     st.error("❌ Invalid Groq API key!")
                
#                 if news_api_key:
#                     if news_valid:
#                         st.session_state.news_api_key = news_api_key
#                         st.success("✅ News API key validated!")
#                     else:
#                         st.error("❌ Invalid News API key!")
#                 else:
#                     st.info("No News API key provided. The app will still work but with limited sources.")
                
#                 # Set API keys valid flag
#                 st.session_state.api_keys_valid = groq_valid
        
#         st.divider()
#         st.markdown("### About")
#         st.markdown("""
#         This app:
#         1. Searches for news articles across multiple sources
#         2. Extracts the content from found articles
#         3. Uses AI to create SEO-optimized summaries
#         """)

#     # Main content area
#     if not st.session_state.api_keys_valid:
#         st.warning("Please enter and validate your Groq API key in the sidebar to continue")
#         st.stop()
    
#     # Search interface
#     st.header("Search for News")
    
#     col1, col2 = st.columns([3, 1])
#     with col1:
#         search_query = st.text_input("Enter a news topic to search", 
#                                     placeholder="e.g., climate change, technology, sports")
    
#     with col2:
#         max_articles = st.number_input("Number of articles", min_value=1, max_value=10, value=3)
    
#     if st.button("Search & Summarize", type="primary"):
#         if not search_query:
#             st.error("Please enter a search query")
#             st.stop()
            
#         # Search for articles
#         st.session_state.search_results = multi_source_news_search(
#             search_query, 
#             max_articles, 
#             st.session_state.get('news_api_key')
#         )
        
#         if not st.session_state.search_results:
#             st.error("No articles found. Try another search query.")
#             st.stop()
    
#     # Display search results
#     if st.session_state.search_results:
#         st.header("Search Results")
        
#         for i, result in enumerate(st.session_state.search_results):
#             st.subheader(f"{i+1}. {result['title']}")
#             st.write(f"**Source:** {result.get('source', 'Unknown')}")
#             st.write(f"**URL:** [{result['url']}]({result['url']})")
            
#             # Article actions
#             if st.button("Scrape & Summarize", key=f"scrape_{i}"):
#                 # Scrape the article
#                 scraped_data = scrape_news_article(result['url'])
                
#                 if scraped_data and scraped_data.get("text"):
#                     # Display article details in tabs to avoid nesting expanders
#                     tabs = st.tabs(["Article Details", "Raw Content", "Summary"])
                    
#                     # Tab 1: Article metadata
#                     with tabs[0]:
#                         st.write(f"**Title:** {scraped_data['title']}")
#                         st.write(f"**Published:** {scraped_data['publish_date']}")
#                         st.write(f"**Source:** {scraped_data['source']}")
#                         st.write(f"**URL:** [{scraped_data['url']}]({scraped_data['url']})")
                    
#                     # Tab 2: Raw content
#                     with tabs[1]:
#                         st.text_area("Content Preview", scraped_data['text'][:1000] + "..." if len(scraped_data['text']) > 1000 else scraped_data['text'], height=300)
                    
#                     # Generate summary
#                     summary = summarize_article(scraped_data, search_query, st.session_state.llm)
                    
#                     # Tab 3: Summary
#                     with tabs[2]:
#                         if summary:
#                             st.markdown(summary)
                            
#                             # Add download button for the summary
#                             st.download_button(
#                                 label="Download Summary",
#                                 data=summary,
#                                 file_name=f"summary_{i+1}.md",
#                                 mime="text/markdown"
#                             )
#                         else:
#                             st.error("Could not generate summary, text may be too short or inadequate.")
#                 else:
#                     st.error("Could not scrape article content.")
            
#             # Add separator between articles
#             st.divider()

# if __name__ == "__main__":
#     main()











# new api, bing news search and duckduckgo search   2

# import streamlit as st
# import os
# import re
# import requests
# import time
# import random
# from typing import Dict, List
# from bs4 import BeautifulSoup
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_groq import ChatGroq
# from langchain_community.document_loaders import WebBaseLoader

# st.set_page_config(
#     page_title="News Scraper & Summarizer",
#     page_icon="📰",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Session state initialization
# if 'search_results' not in st.session_state:
#     st.session_state.search_results = []
# if 'api_keys_valid' not in st.session_state:
#     st.session_state.api_keys_valid = False
# if 'llm' not in st.session_state:
#     st.session_state.llm = None

# # Define user agents to rotate
# USER_AGENTS = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
#     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# ]

# # Function definitions
# def get_random_headers():
#     """Get random headers to avoid detection"""
#     return {
#         'User-Agent': random.choice(USER_AGENTS),
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.5',
#         'Referer': 'https://www.google.com/',
#         'DNT': '1',
#         'Connection': 'keep-alive',
#         'Upgrade-Insecure-Requests': '1',
#         'Sec-Fetch-Dest': 'document',
#         'Sec-Fetch-Mode': 'navigate',
#         'Sec-Fetch-Site': 'none',
#         'Sec-Fetch-User': '?1',
#         'Cache-Control': 'max-age=0'
#     }

# def search_duckduckgo_news(query: str, max_results: int = 3):
#     """Search news using DuckDuckGo"""
#     search_url = f"https://duckduckgo.com/html/?q={query}+news"
#     headers = get_random_headers()
   
#     try:
#         with st.spinner(f"Searching DuckDuckGo for: {query}"):
#             response = requests.get(search_url, headers=headers)
#             response.raise_for_status()
           
#             soup = BeautifulSoup(response.text, 'html.parser')
#             results = []
           
#             # Extract links from search results
#             for result in soup.select('.result__a'):
#                 link = result.get('href')
#                 if link:
#                     # Clean up URL
#                     if '/l/?uddg=' in link:
#                         # Extract the actual URL from DuckDuckGo's redirect
#                         decoded_url = link.split('/l/?uddg=')[1].split('&')[0]
#                         link = requests.utils.unquote(decoded_url)
                    
#                     # Try to get snippet
#                     snippet = ""
#                     snippet_element = result.find_next('.result__snippet')
#                     if snippet_element:
#                         snippet = snippet_element.text.strip()
                   
#                     results.append({
#                         "title": result.text.strip(),
#                         "url": link,
#                         "source": link.split('/')[2] if '//' in link else "Unknown source",
#                         "snippet": snippet
#                     })
                   
#                     if len(results) >= max_results:
#                         break
                       
#             return results
#     except Exception as e:
#         st.error(f"DuckDuckGo search error: {e}")
#         return []

# def search_bing_news(query: str, max_results: int = 3):
#     """Search news using Bing"""
#     search_url = f"https://www.bing.com/news/search?q={query.replace(' ', '+')}"
#     headers = get_random_headers()
   
#     try:
#         with st.spinner(f"Searching Bing News for: {query}"):
#             response = requests.get(search_url, headers=headers)
#             response.raise_for_status()
           
#             soup = BeautifulSoup(response.text, 'html.parser')
#             results = []
           
#             # Extract news articles
#             for article in soup.select('.news-card'):
#                 link_element = article.select_one('a.title')
#                 if link_element:
#                     link = link_element.get('href')
#                     title = link_element.text.strip()
                   
#                     source_element = article.select_one('.source')
#                     source = source_element.text.strip() if source_element else "Unknown"
                   
#                     snippet_element = article.select_one('.snippet')
#                     snippet = snippet_element.text.strip() if snippet_element else ""
                   
#                     if link and link.startswith('http'):
#                         results.append({
#                             "title": title,
#                             "url": link,
#                             "source": source,
#                             "snippet": snippet
#                         })
                       
#                         if len(results) >= max_results:
#                             break
           
#             return results
#     except Exception as e:
#         st.error(f"Bing News search error: {e}")
#         return []

# def news_api_search(query: str, max_results: int = 3, api_key: str = None):
#     """Search using NewsAPI if API key is available"""
#     if not api_key:
#         st.warning("NEWS_API_KEY not provided, skipping NewsAPI search")
#         return []
       
#     url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={api_key}"
   
#     try:
#         with st.spinner(f"Searching NewsAPI for: {query}"):
#             response = requests.get(url)
#             response.raise_for_status()
#             data = response.json()
           
#             results = []
#             if data["status"] == "ok" and data["totalResults"] > 0:
#                 for article in data["articles"][:max_results]:
#                     results.append({
#                         "title": article["title"],
#                         "url": article["url"],
#                         "source": article["source"]["name"],
#                         "snippet": article["description"] or "",
#                         "publish_date": article.get("publishedAt", "Unknown")
#                     })
#             return results
#     except Exception as e:
#         st.error(f"NewsAPI search error: {e}")
#         return []

# def search_raw_html(url: str, query: str, max_results: int = 3):
#     """Extract links from raw HTML of a news site"""
#     headers = get_random_headers()
   
#     try:
#         with st.spinner(f"Searching {url} for: {query}"):
#             response = requests.get(url, headers=headers)
#             response.raise_for_status()
           
#             # Find all links
#             soup = BeautifulSoup(response.text, 'html.parser')
#             results = []
           
#             # Look for links that might contain the query terms
#             query_terms = query.lower().split()
#             links = soup.find_all('a', href=True)
           
#             for link in links:
#                 href = link.get('href')
#                 text = link.text.strip()
               
#                 # Skip empty links, navigation, etc.
#                 if (not href or not text or len(text) < 15 or
#                     href.startswith('#') or 'javascript:' in href):
#                     continue
                   
#                 # Make absolute URL if needed
#                 if href.startswith('/'):
#                     href = f"{url.split('//', 1)[0]}//{url.split('//', 1)[1].split('/', 1)[0]}{href}"
#                 elif not href.startswith(('http://', 'https://')):
#                     continue
                   
#                 # Check if link text contains any query terms
#                 if any(term in text.lower() for term in query_terms):
#                     # Try to find snippet near the link
#                     snippet = ""
#                     if link.parent and link.parent.text:
#                         full_text = link.parent.text.strip()
#                         if len(full_text) > len(text):
#                             snippet = full_text
                    
#                     results.append({
#                         "title": text,
#                         "url": href,
#                         "source": href.split('/')[2] if '//' in href else "Unknown",
#                         "snippet": snippet
#                     })
                   
#                     if len(results) >= max_results:
#                         break
                       
#             return results
#     except Exception as e:
#         st.error(f"Raw HTML search error for {url}: {e}")
#         return []

# def multi_source_news_search(query: str, max_articles: int = 3, news_api_key: str = None) -> List[Dict]:
#     """Search multiple news sources and aggregate results"""
#     all_results = []
    
#     progress_bar = st.progress(0)
#     progress_text = st.empty()
    
#     # Try NewsAPI first if available
#     if news_api_key:
#         progress_text.text("Searching NewsAPI...")
#         results = news_api_search(query, max_articles, news_api_key)
#         if results:
#             st.success(f"Found {len(results)} results from NewsAPI")
#             all_results.extend(results)
#         progress_bar.progress(0.25)
   
#     # If we don't have enough results, try Bing News
#     if len(all_results) < max_articles:
#         progress_text.text("Searching Bing News...")
#         remaining = max_articles - len(all_results)
#         results = search_bing_news(query, remaining)
#         if results:
#             st.success(f"Found {len(results)} results from Bing News")
#             all_results.extend(results)
#         progress_bar.progress(0.5)
   
#     # If we still don't have enough, try DuckDuckGo
#     if len(all_results) < max_articles:
#         progress_text.text("Searching DuckDuckGo...")
#         remaining = max_articles - len(all_results)
#         results = search_duckduckgo_news(query, remaining)
#         if results:
#             st.success(f"Found {len(results)} results from DuckDuckGo")
#             all_results.extend(results)
#         progress_bar.progress(0.75)
   
#     # If still not enough, try some specific news sites directly
#     if len(all_results) < max_articles:
#         progress_text.text("Searching direct news sites...")
#         news_sites = [
#             "https://news.yahoo.com",
#             "https://www.reuters.com",
#             "https://www.bbc.com/news"
#         ]
       
#         for site in news_sites:
#             if len(all_results) >= max_articles:
#                 break
               
#             remaining = max_articles - len(all_results)
#             results = search_raw_html(site, query, remaining)
#             if results:
#                 st.success(f"Found {len(results)} results from {site}")
#                 all_results.extend(results)
    
#     progress_bar.progress(1.0)
#     progress_text.empty()
   
#     # Deduplicate by URL
#     unique_results = []
#     seen_urls = set()
   
#     for result in all_results:
#         if result["url"] not in seen_urls:
#             seen_urls.add(result["url"])
#             unique_results.append(result)
   
#     return unique_results[:max_articles]

# # Scrape individual news article
# def scrape_news_article(url: str) -> Dict:
#     with st.spinner(f"Scraping article: {url}"):
#         headers = get_random_headers()
       
#         try:
#             # First try with WebBaseLoader
#             loader = WebBaseLoader(
#                 web_paths=[url],
#                 requests_kwargs={"headers": headers}
#             )
#             document = loader.load()[0]
#             text = document.page_content.strip()
#             metadata = document.metadata
           
#             # If text is too short, try with direct requests + BeautifulSoup
#             if len(text) < 50:
#                 st.info("Content too short, trying direct parsing...")
#                 response = requests.get(url, headers=headers)
#                 response.raise_for_status()
               
#                 soup = BeautifulSoup(response.text, 'html.parser')
               
#                 # Remove script, style elements
#                 for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
#                     element.decompose()
                   
#                 # Get title
#                 title = soup.title.text.strip() if soup.title else "Untitled"
               
#                 # Extract main content
#                 article_text = ""
               
#                 # Try common article content selectors
#                 selectors = [
#                     'article', '.article', '.content', '.story', 'main',
#                     '.post-content', '.entry-content', '#content'
#                 ]
               
#                 for selector in selectors:
#                     content = soup.select_one(selector)
#                     if content:
#                         paragraphs = content.find_all('p')
#                         article_text = '\n\n'.join([p.text.strip() for p in paragraphs])
#                         if len(article_text) > 500:  # Only use if substantial content found
#                             break
                           
#                 # If still no good content, just use all paragraphs
#                 if len(article_text) < 500:
#                     paragraphs = soup.find_all('p')
#                     article_text = '\n\n'.join([p.text.strip() for p in paragraphs])
                   
#                 # Look for publish date
#                 date = None
#                 date_selectors = ['time', '.date', '.published', 'meta[property="article:published_time"]']
#                 for selector in date_selectors:
#                     date_element = soup.select_one(selector)
#                     if date_element:
#                         if date_element.name == 'meta':
#                             date = date_element.get('content', '')
#                         else:
#                             date = date_element.text.strip()
#                         break
                       
#                 return {
#                     "title": title,
#                     "text": article_text,
#                     "snippet": article_text[:200] + "..." if len(article_text) > 200 else article_text,
#                     "publish_date": date or "Unknown",
#                     "source": url.split('/')[2],
#                     "url": url
#                 }
           
#             return {
#                 "title": metadata.get("title", "Untitled"),
#                 "text": text,
#                 "snippet": text[:200] + "..." if len(text) > 200 else text,
#                 "publish_date": metadata.get("publish_date", "Unknown"),
#                 "source": url.split('/')[2],
#                 "url": url
#             }
#         except Exception as e:
#             st.error(f"Error scraping {url}: {e}")
#             return None

# # Summarize article with fallback to snippet if text is not available
# def summarize_article(article_data: Dict, topic: str, llm, original_result: Dict = None) -> str:
#     # Check if we have article text
#     article_text = article_data.get("text", "").strip() if article_data else ""
    
#     # If article text is too short or not available, fall back to snippet from search results
#     if not article_data or len(article_text) < 100:
#         if original_result and original_result.get("snippet"):
#             st.warning("Full article text not available. Using snippet for summarization.")
#             article_text = original_result.get("snippet")
            
#             # If still no good content, cannot summarize
#             if len(article_text) < 50:
#                 return None
                
#             # Create minimal article data from snippet
#             if not article_data:
#                 article_data = {
#                     "title": original_result.get("title", "Unknown Title"),
#                     "url": original_result.get("url", ""),
#                     "source": original_result.get("source", "Unknown Source"),
#                     "publish_date": original_result.get("publish_date", "Unknown"),
#                     "text": article_text
#                 }
#         else:
#             return None
   
#     # Limit article text length to prevent token limits
#     if len(article_text) > 15000:
#         article_text = article_text[:15000] + "..."

#     with st.spinner("Generating summary..."):
#         template = """
#         Create an SEO-optimized news summary:
     
#         ARTICLE CONTENT: {article_text}
#         TITLE: {article_title}
#         PUBLISHED: {publish_date}
#         URL: {article_url}
#         TOPIC: {topic}
     
#         REQUIREMENTS:
#         - Title: Custom, SEO-optimized
#         - Length: 300-500 words
#         - Structure: Lead paragraph, context, key facts
#         - Keywords: [KEYWORDS: relevant, keywords]
     
#         OUTPUT:
#         ## [Title]
     
#         [Summary]
     
#         **Source:** [Source Name] ([article_url])
#         **Published Date:** [publish_date]
#         [KEYWORDS: keyword1, keyword2]
#         """
     
#         prompt = ChatPromptTemplate.from_template(template)
#         chain = prompt | llm | StrOutputParser()
     
#         try:
#             return chain.invoke({
#                 "article_text": article_text,
#                 "article_title": article_data["title"],
#                 "publish_date": article_data["publish_date"],
#                 "article_url": article_data["url"],
#                 "topic": topic
#             })
#         except Exception as e:
#             st.error(f"Error summarizing article: {e}")
#             return None

# def validate_groq_api_key(api_key):
#     """Validate the GROQ API key by making a simple request"""
#     if not api_key:
#         return False
    
#     try:
#         # Just initialize the client to check
#         llm = ChatGroq(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             api_key=api_key
#         )
#         return True
#     except Exception as e:
#         st.error(f"Invalid GROQ API key: {e}")
#         return False

# def validate_news_api_key(api_key):
#     """Validate the NewsAPI key by making a simple request"""
#     if not api_key:
#         # NewsAPI is optional, so we return True if not provided
#         return True
    
#     url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
#     try:
#         response = requests.get(url)
#         data = response.json()
#         if data.get("status") == "ok":
#             return True
#         else:
#             st.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
#             return False
#     except Exception as e:
#         st.error(f"Failed to validate NewsAPI key: {e}")
#         return False

# # Main Streamlit app
# def main():
#     st.title("📰 News Scraper & Summarizer")
    
#     # Sidebar for API keys
#     with st.sidebar:
#         st.header("API Keys")
        
#         # Groq API Key (required)
#         groq_api_key = st.text_input("Groq API Key (required)", 
#                                      value=st.session_state.get('groq_api_key', ''),
#                                      type="password",
#                                      help="Required for summarization. Get one from https://console.groq.com/")
        
#         # News API Key (optional)
#         news_api_key = st.text_input("News API Key (optional)", 
#                                     value=st.session_state.get('news_api_key', ''),
#                                     type="password",
#                                     help="Optional for better news search. Get one from https://newsapi.org/")
        
#         if st.button("Validate API Keys"):
#             with st.spinner("Validating API keys..."):
#                 groq_valid = validate_groq_api_key(groq_api_key)
#                 news_valid = validate_news_api_key(news_api_key)
                
#                 if groq_valid:
#                     st.session_state.groq_api_key = groq_api_key
#                     st.session_state.llm = ChatGroq(
#                         model="meta-llama/llama-4-scout-17b-16e-instruct",
#                         api_key=groq_api_key
#                     )
#                     st.success("✅ Groq API key validated!")
#                 else:
#                     st.error("❌ Invalid Groq API key!")
                
#                 if news_api_key:
#                     if news_valid:
#                         st.session_state.news_api_key = news_api_key
#                         st.success("✅ News API key validated!")
#                     else:
#                         st.error("❌ Invalid News API key!")
#                 else:
#                     st.info("No News API key provided. The app will still work but with limited sources.")
                
#                 # Set API keys valid flag
#                 st.session_state.api_keys_valid = groq_valid
        
#         st.divider()
#         st.markdown("### About")
#         st.markdown("""
#         This app:
#         1. Searches for news articles across multiple sources
#         2. Extracts the content from found articles
#         3. Uses AI to create SEO-optimized summaries
#         """)

#     # Main content area
#     if not st.session_state.api_keys_valid:
#         st.warning("Please enter and validate your Groq API key in the sidebar to continue")
#         st.stop()
    
#     # Search interface
#     st.header("Search for News")
    
#     col1, col2 = st.columns([3, 1])
#     with col1:
#         search_query = st.text_input("Enter a news topic to search", 
#                                     placeholder="e.g., climate change, technology, sports")
    
#     with col2:
#         max_articles = st.number_input("Number of articles", min_value=1, max_value=10, value=3)
    
#     if st.button("Search & Summarize", type="primary"):
#         if not search_query:
#             st.error("Please enter a search query")
#             st.stop()
            
#         # Search for articles
#         st.session_state.search_results = multi_source_news_search(
#             search_query, 
#             max_articles, 
#             st.session_state.get('news_api_key')
#         )
        
#         if not st.session_state.search_results:
#             st.error("No articles found. Try another search query.")
#             st.stop()
    
#     # Display search results
#     if st.session_state.search_results:
#         st.header("Search Results")
        
#         for i, result in enumerate(st.session_state.search_results):
#             st.subheader(f"{i+1}. {result['title']}")
#             st.write(f"**Source:** {result.get('source', 'Unknown')}")
#             st.write(f"**URL:** [{result['url']}]({result['url']})")
            
#             # Show snippet if available
#             if result.get('snippet'):
#                 with st.expander("Snippet"):
#                     st.write(result['snippet'])
            
#             # Article actions
#             if st.button("Scrape & Summarize", key=f"scrape_{i}"):
#                 # Scrape the article
#                 scraped_data = scrape_news_article(result['url'])
                
#                 # Process article data
#                 if scraped_data:
#                     # Display article details in tabs
#                     tabs = st.tabs(["Article Details", "Raw Content", "Summary"])
                    
#                     # Tab 1: Article metadata with added published date and snippet
#                     with tabs[0]:
#                         st.write(f"**Title:** {scraped_data['title']}")
#                         st.write(f"**Published:** {scraped_data['publish_date']}")
#                         st.write(f"**Source:** {scraped_data['source']}")
#                         st.write(f"**URL:** [{scraped_data['url']}]({scraped_data['url']})")
                        
#                         # Add snippet from search result if available
#                         if result.get('snippet'):
#                             st.write("**Search Snippet:**")
#                             st.write(result['snippet'])
                        
#                         # Add snippet from scraped data if available
#                         if scraped_data.get('snippet'):
#                             st.write("**Content Snippet:**")
#                             st.write(scraped_data['snippet'])
                    
#                     # Tab 2: Raw content
#                     with tabs[1]:
#                         if scraped_data.get('text') and len(scraped_data['text']) > 0:
#                             st.text_area("Content Preview", 
#                                          scraped_data['text'][:1000] + "..." if len(scraped_data['text']) > 1000 else scraped_data['text'], 
#                                          height=300)
#                         else:
#                             st.warning("No article text could be extracted.")
#                             if result.get('snippet'):
#                                 st.write("**Using search snippet instead:**")
#                                 st.write(result['snippet'])
                    
#                     # Generate summary using article text or falling back to snippet
#                     summary = summarize_article(scraped_data, search_query, st.session_state.llm, result)
                    
#                     # Tab 3: Summary
#                     with tabs[2]:
#                         if summary:
#                             st.markdown(summary)
                            
#                             # Add download button for the summary
#                             st.download_button(
#                                 label="Download Summary",
#                                 data=summary,
#                                 file_name=f"summary_{i+1}.md",
#                                 mime="text/markdown"
#                             )
#                         else:
#                             st.error("Could not generate a summary. Not enough content available.")
#                 else:
#                     st.error("Could not scrape article content.")
                    
#                     # Try to use snippet for summarization if available
#                     if result.get('snippet') and len(result['snippet']) > 50:
#                         st.warning("Attempting to summarize using search snippet only...")
                        
#                         # Create minimal article data from snippet
#                         minimal_data = {
#                             "title": result.get("title", "Unknown Title"),
#                             "url": result.get("url", ""),
#                             "source": result.get("source", "Unknown Source"),
#                             "publish_date": result.get("publish_date", "Unknown"),
#                             "text": result.get("snippet", "")
#                         }
                        
#                         summary = summarize_article(minimal_data, search_query, st.session_state.llm)
                        
#                         if summary:
#                             st.markdown("## Summary from Snippet")
#                             st.markdown(summary)
                            
#                             # Add download button for the summary
#                             st.download_button(
#                                 label="Download Summary",
#                                 data=summary,
#                                 file_name=f"summary_{i+1}.md",
#                                 mime="text/markdown"
#                             )
#                         else:
#                             st.error("Could not generate a summary from the snippet.")
            
#             # Add separator between articles
#             st.divider()

# if __name__ == "__main__":
#     main()











# new api, bing news search and duckduckgo search and then specific news sites   3


import streamlit as st
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
from datetime import datetime

st.set_page_config(
    page_title="News Scraper & Summarizer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'api_keys_valid' not in st.session_state:
    st.session_state.api_keys_valid = False
if 'llm' not in st.session_state:
    st.session_state.llm = None

# Define user agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

# Function definitions
def get_random_headers():
    """Get random headers to avoid detection"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
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

def parse_date(date_str):
    """Parse various date formats into a consistent format"""
    if not date_str:
        return "Unknown"
    
    try:
        # Try ISO format first (from NewsAPI)
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%B %d, %Y %H:%M")
    except ValueError:
        pass
    
    # Try other common formats
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d %B %Y", "%b %d, %Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%B %d, %Y %H:%M")
        except ValueError:
            pass
    
    # If all parsing fails, return original string
    return date_str

def search_duckduckgo_news(query: str, max_results: int = 3):
    """Search news using DuckDuckGo"""
    search_url = f"https://duckduckgo.com/html/?q={query}+news"
    headers = get_random_headers()
   
    try:
        with st.spinner(f"Searching DuckDuckGo for: {query}"):
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
                    
                    # Try to get snippet
                    snippet = ""
                    snippet_element = result.find_next('.result__snippet')
                    if snippet_element:
                        snippet = snippet_element.text.strip()
                    
                    # Try to get date (DuckDuckGo doesn't always show dates)
                    date = "Unknown"
                    date_element = result.find_next(class_='result__timestamp')
                    if date_element:
                        date = parse_date(date_element.text.strip())

                    # Debugging
                    print(f"{"="*15} DUCKDUCKGO SEARCH {"="*15}")
                    print("title found: ", result.text.strip())
                    print("Snippet found: ", snippet)
                    print("publish_date", date)
                   
                    results.append({
                        "title": result.text.strip(),
                        "url": link,
                        "source": link.split('/')[2] if '//' in link else "Unknown source",
                        "snippet": snippet,
                        "publish_date": date
                    })
                   
                    if len(results) >= max_results:
                        break
                       
            return results
    except Exception as e:
        st.error(f"DuckDuckGo search error: {e}")
        return []

def search_bing_news(query: str, max_results: int = 3):
    """Search news using Bing"""
    search_url = f"https://www.bing.com/news/search?q={query.replace(' ', '+')}"
    headers = get_random_headers()
   
    try:
        with st.spinner(f"Searching Bing News for: {query}"):
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
                    
                    # Extract date from Bing News
                    date = "Unknown"
                    date_element = article.select_one('.time')
                    if date_element:
                        date = parse_date(date_element.text.strip())


                    # Debugging
                    print(f"{"="*15} BING NEWS SEARCH {"="*15}")
                    print("title found: ", title)
                    print("Snippet found: ", snippet)
                    print("publish_date", date)
                   
                    if link and link.startswith('http'):
                        results.append({
                            "title": title,
                            "url": link,
                            "source": source,
                            "snippet": snippet,
                            "publish_date": date
                        })
                       
                        if len(results) >= max_results:
                            break
           
            return results
    except Exception as e:
        st.error(f"Bing News search error: {e}")
        return []

def news_api_search(query: str, max_results: int = 3, api_key: str = None):
    """Search using NewsAPI if API key is available"""
    if not api_key:
        st.warning("NEWS_API_KEY not provided, skipping NewsAPI search")
        return []
       
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={api_key}"
   
    try:
        with st.spinner(f"Searching NewsAPI for: {query}"):
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
           
            results = []
            if data["status"] == "ok" and data["totalResults"] > 0:
                for article in data["articles"][:max_results]:

                    # Debugging
                    print(f"{"="*15} NEWS API {"="*15}")
                    print("title found: ", article["title"])
                    print("Snippet found: ", article["description"] or "")
                    print("publish_date", parse_date(article.get("publishedAt", "Unknown")))

                    results.append({
                        "title": article["title"],
                        "url": article["url"],
                        "source": article["source"]["name"],
                        "snippet": article["description"] or "",
                        "publish_date": parse_date(article.get("publishedAt", "Unknown"))
                    })
            return results
    except Exception as e:
        st.error(f"NewsAPI search error: {e}")
        return []

def search_raw_html(url: str, query: str, max_results: int = 3):
    """Extract links from raw HTML of a news site"""
    headers = get_random_headers()
   
    try:
        with st.spinner(f"Searching {url} for: {query}"):
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
                    # Try to find snippet near the link
                    snippet = ""
                    if link.parent and link.parent.text:
                        full_text = link.parent.text.strip()
                        if len(full_text) > len(text):
                            snippet = full_text
                    
                    # Debugging
                    print(f"{"="*15} RAW HTML {"="*15}")
                    print("title found: ", text)
                    print("Snippet found: ", snippet)
                    print("publish_date", "Unknown")

                    results.append({
                        "title": text,
                        "url": href,
                        "source": href.split('/')[2] if '//' in href else "Unknown",
                        "snippet": snippet,
                        "publish_date": "Unknown"  # Can't get date from raw HTML
                    })
                   
                    if len(results) >= max_results:
                        break
                       
            return results
    except Exception as e:
        st.error(f"Raw HTML search error for {url}: {e}")
        return []

def multi_source_news_search(query: str, max_articles: int = 3, news_api_key: str = None) -> List[Dict]:
    """Search multiple news sources and aggregate results"""
    all_results = []
    
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    # Try NewsAPI first if available
    if news_api_key:
        progress_text.text("Searching NewsAPI...")
        results = news_api_search(query, max_articles, news_api_key)
        if results:
            st.success(f"Found {len(results)} results from NewsAPI")
            all_results.extend(results)
        progress_bar.progress(0.25)
   
    # If we don't have enough results, try Bing News
    if len(all_results) < max_articles:
        progress_text.text("Searching Bing News...")
        remaining = max_articles - len(all_results)
        results = search_bing_news(query, remaining)
        if results:
            st.success(f"Found {len(results)} results from Bing News")
            all_results.extend(results)
        progress_bar.progress(0.5)
   
    # If we still don't have enough, try DuckDuckGo
    if len(all_results) < max_articles:
        progress_text.text("Searching DuckDuckGo...")
        remaining = max_articles - len(all_results)
        results = search_duckduckgo_news(query, remaining)
        if results:
            st.success(f"Found {len(results)} results from DuckDuckGo")
            all_results.extend(results)
        progress_bar.progress(0.75)
   
    # If still not enough, try some specific news sites directly
    if len(all_results) < max_articles:
        progress_text.text("Searching direct news sites...")
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
                st.success(f"Found {len(results)} results from {site}")
                all_results.extend(results)
    
    progress_bar.progress(1.0)
    progress_text.empty()
   
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
    with st.spinner(f"Scraping article: {url}"):
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
                st.info("Content too short, trying direct parsing...")
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
                        if len(article_text) > 100:  #500 # Only use if substantial content found
                            break
                           
                # If still no good content, just use all paragraphs
                if len(article_text) < 100:  #500
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
                    "snippet": article_text, #[:200], # + "..." if len(article_text) > 200 else article_text,
                    "publish_date": parse_date(date) if date else "Unknown",
                    "source": url.split('/')[2],
                    "url": url
                }
           
            return {
                "title": metadata.get("title", "Untitled"),
                "text": text,
                "snippet": text, #[:200], # + "..." if len(text) > 200 else text,
                "publish_date": parse_date(metadata.get("publish_date", "Unknown")),
                "source": url.split('/')[2],
                "url": url
            }
        except Exception as e:
            st.error(f"Error scraping {url}: {e}")
            return None

# Summarize article with fallback to snippet if text is not available
def summarize_article(article_data: Dict, topic: str, llm, original_result: Dict = None) -> str:
    # Check if we have article text
    article_text = article_data.get("text", "").strip() if article_data else ""
    
    # If article text is too short or not available, fall back to snippet from search results
    if not article_data or len(article_text) < 50:
        if original_result and original_result.get("snippet"):
            st.warning("Full article text not available. Using snippet for summarization.")
            article_text = original_result.get("snippet")
            
            # If still no good content, cannot summarize
            if len(article_text) < 50:
                return None
                
            # Create minimal article data from snippet
            if not article_data:
                article_data = {
                    "title": original_result.get("title", "Unknown Title"),
                    "url": original_result.get("url", ""),
                    "source": original_result.get("source", "Unknown Source"),
                    "publish_date": original_result.get("publish_date", "Unknown"),
                    "text": article_text
                }
        else:
            return None
   
    # Limit article text length to prevent token limits
    if len(article_text) > 15000:
        article_text = article_text[:15000] + "..."

    with st.spinner("Generating summary..."):
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
        - Include the published date prominently
     
        OUTPUT Format:
        ## [Title]
     
        [Summary] with [article content]

        **Source:** [Source Name] ([article_url])\n
        **Published Date:** {publish_date}\n
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
            st.error(f"Error summarizing article: {e}")
            return None

def validate_groq_api_key(api_key):
    """Validate the GROQ API key by making a simple request"""
    if not api_key:
        return False
    
    try:
        # Just initialize the client to check
        llm = ChatGroq(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            api_key=api_key
        )
        return True
    except Exception as e:
        st.error(f"Invalid GROQ API key: {e}")
        return False

def validate_news_api_key(api_key):
    """Validate the NewsAPI key by making a simple request"""
    if not api_key:
        # NewsAPI is optional, so we return True if not provided
        return True
    
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("status") == "ok":
            return True
        else:
            st.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Failed to validate NewsAPI key: {e}")
        return False

# Main Streamlit app
def main():
    st.title("📰 News Scraper & Summarizer")
    
    # Sidebar for API keys
    with st.sidebar:
        st.header("API Keys")
        
        # Groq API Key (required)
        groq_api_key = st.text_input("Groq API Key (required)", 
                                     value=st.session_state.get('groq_api_key', ''),
                                     type="password",
                                     help="Required for summarization. Get one from https://console.groq.com/")
        
        # News API Key (optional)
        news_api_key = st.text_input("News API Key (optional)", 
                                    value=st.session_state.get('news_api_key', ''),
                                    type="password",
                                    help="Optional for better news search. Get one from https://newsapi.org/")
        
        if st.button("Validate API Keys"):
            with st.spinner("Validating API keys..."):
                groq_valid = validate_groq_api_key(groq_api_key)
                news_valid = validate_news_api_key(news_api_key)
                
                if groq_valid:
                    st.session_state.groq_api_key = groq_api_key
                    st.session_state.llm = ChatGroq(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        api_key=groq_api_key
                    )
                    st.success("✅ Groq API key validated!")
                else:
                    st.error("❌ Invalid Groq API key!")
                
                if news_api_key:
                    if news_valid:
                        st.session_state.news_api_key = news_api_key
                        st.success("✅ News API key validated!")
                    else:
                        st.error("❌ Invalid News API key!")
                else:
                    st.info("No News API key provided. The app will still work but with limited sources.")
                
                # Set API keys valid flag
                st.session_state.api_keys_valid = groq_valid
        
        st.divider()
        st.markdown("### About")
        st.markdown("""
        This app:
        1. Searches for news articles across multiple sources
        2. Extracts the content from found articles
        3. Uses AI to create SEO-optimized summaries
        """)

    # Main content area
    if not st.session_state.api_keys_valid:
        st.warning("Please enter and validate your Groq API key in the sidebar to continue")
        st.stop()
    
    # Search interface
    st.header("Search for News")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Enter a news topic to search", 
                                    placeholder="e.g., climate change, technology, sports",
                                    key="search_input",
                                    on_change=lambda: perform_search() if st.session_state.get('search_input') else None)
    
    with col2:
        max_articles = st.number_input("Number of articles", min_value=1, max_value=10, value=3)
    
    def perform_search():
        if not st.session_state.get('search_input'):
            st.error("Please enter a search query")
            return
            
        # Search for articles
        st.session_state.search_results = multi_source_news_search(
            st.session_state.search_input, 
            max_articles, 
            st.session_state.get('news_api_key')
        )
        
        if not st.session_state.search_results:
            st.error("No articles found. Try another search query.")
    
    if st.button("Search & Summarize", type="primary") or st.session_state.get('trigger_search', False):
        st.session_state.trigger_search = False
        perform_search()
    
    # Display search results
    if st.session_state.search_results:
        st.header("Search Results")
        
        for i, result in enumerate(st.session_state.search_results):
            st.subheader(f"{i+1}. {result['title']}")
            st.write(f"**Source:** {result.get('source', 'Unknown')}")
            st.write(f"**Published:** {result.get('publish_date', 'Unknown')}")
            st.write(f"**URL:** [{result['url']}]({result['url']})")
            
            # Show snippet if available
            if result.get('snippet'):
                with st.expander("Snippet"):
                    st.write(result['snippet'])
            
            # Article actions
            if st.button("Scrape & Summarize", key=f"scrape_{i}"):
                # Scrape the article
                scraped_data = scrape_news_article(result['url'])
                
                # Process article data
                if scraped_data:
                    # Display article details in tabs
                    tabs = st.tabs(["Article Details", "Raw Content", "Summary"])
                    
                    # Tab 1: Article metadata with added published date and snippet
                    with tabs[0]:
                        st.write(f"**Title:** {scraped_data['title']}")
                        st.write(f"**Published:** {scraped_data['publish_date']}")
                        st.write(f"**Source:** {scraped_data['source']}")
                        st.write(f"**URL:** [{scraped_data['url']}]({scraped_data['url']})")
                        
                        # Add snippet from search result if available
                        if result.get('snippet'):
                            st.write("**Search Snippet:**")
                            st.write(result['snippet'])
                        
                        # Add snippet from scraped data if available
                        if scraped_data.get('snippet'):
                            st.write("**Content Snippet:**")
                            st.write(scraped_data['snippet'])
                    
                    # Tab 2: Raw content
                    with tabs[1]:
                        if scraped_data.get('text') and len(scraped_data['text']) > 0:
                            st.text_area("Content Preview", 
                                         scraped_data['text'], #[:1000], #+ "..." if len(scraped_data['text']) > 1000 else scraped_data['text'], 
                                         height=300)
                        else:
                            st.warning("No article text could be extracted.")
                            if result.get('snippet'):
                                st.write("**Using search snippet instead:**")
                                st.write(result['snippet'])
                    
                    # Generate summary using article text or falling back to snippet
                    summary = summarize_article(scraped_data, search_query, st.session_state.llm, result)
                    
                    # Tab 3: Summary
                    with tabs[2]:
                        if summary:
                            st.markdown(summary)
                            
                            # Add download button for the summary
                            st.download_button(
                                label="Download Summary",
                                data=summary,
                                file_name=f"summary_{i+1}.md",
                                mime="text/markdown"
                            )
                        else:
                            st.error("Could not generate a summary. Not enough content available.")
                else:
                    st.error("Could not scrape article content.")
                    
                    # Try to use snippet for summarization if available
                    if result.get('snippet') and len(result['snippet']) > 50:
                        st.warning("Attempting to summarize using search snippet only...")
                        
                        # Create minimal article data from snippet
                        minimal_data = {
                            "title": result.get("title", "Unknown Title"),
                            "url": result.get("url", ""),
                            "source": result.get("source", "Unknown Source"),
                            "publish_date": result.get("publish_date", "Unknown"),
                            "text": result.get("snippet", "")
                        }
                        
                        summary = summarize_article(minimal_data, search_query, st.session_state.llm)
                        
                        if summary:
                            st.markdown("## Summary from Snippet")
                            st.markdown(summary)
                            
                            # Add download button for the summary
                            st.download_button(
                                label="Download Summary",
                                data=summary,
                                file_name=f"summary_{i+1}.md",
                                mime="text/markdown"
                            )
                        else:
                            st.error("Could not generate a summary from the snippet.")
            
            # Add separator between articles
            st.divider()

if __name__ == "__main__":
    main()









# # first is duckduckgo, bing search, newapi and then specific news sites  1

# import streamlit as st
# import os
# import re
# import requests
# import time
# import random
# from typing import Dict, List
# from bs4 import BeautifulSoup
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_groq import ChatGroq
# from langchain_community.document_loaders import WebBaseLoader
# from datetime import datetime

# st.set_page_config(
#     page_title="News Scraper & Summarizer",
#     page_icon="📰",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Session state initialization
# if 'search_results' not in st.session_state:
#     st.session_state.search_results = []
# if 'api_keys_valid' not in st.session_state:
#     st.session_state.api_keys_valid = False
# if 'llm' not in st.session_state:
#     st.session_state.llm = None

# # Define user agents to rotate
# USER_AGENTS = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
#     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# ]

# # Function definitions
# def get_random_headers():
#     """Get random headers to avoid detection"""
#     return {
#         'User-Agent': random.choice(USER_AGENTS),
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.5',
#         'Referer': 'https://www.google.com/',
#         'DNT': '1',
#         'Connection': 'keep-alive',
#         'Upgrade-Insecure-Requests': '1',
#         'Sec-Fetch-Dest': 'document',
#         'Sec-Fetch-Mode': 'navigate',
#         'Sec-Fetch-Site': 'none',
#         'Sec-Fetch-User': '?1',
#         'Cache-Control': 'max-age=0'
#     }

# def parse_date(date_str):
#     """Parse various date formats into a consistent format"""
#     if not date_str:
#         return "Unknown"
    
#     try:
#         # Try ISO format first (from NewsAPI)
#         dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
#         return dt.strftime("%B %d, %Y %H:%M")
#     except ValueError:
#         pass
    
#     # Try other common formats
#     for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d %B %Y", "%b %d, %Y"):
#         try:
#             dt = datetime.strptime(date_str, fmt)
#             return dt.strftime("%B %d, %Y %H:%M")
#         except ValueError:
#             pass
    
#     # If all parsing fails, return original string
#     return date_str

# def search_duckduckgo_news(query: str, max_results: int = 3):
#     """Search news using DuckDuckGo"""
#     search_url = f"https://duckduckgo.com/html/?q={query}+news"
#     headers = get_random_headers()
   
#     try:
#         with st.spinner(f"Searching DuckDuckGo for: {query}"):
#             response = requests.get(search_url, headers=headers)
#             response.raise_for_status()
           
#             soup = BeautifulSoup(response.text, 'html.parser')
#             results = []
           
#             # Extract links from search results
#             for result in soup.select('.result__a'):
#                 link = result.get('href')
#                 if link:
#                     # Clean up URL
#                     if '/l/?uddg=' in link:
#                         # Extract the actual URL from DuckDuckGo's redirect
#                         decoded_url = link.split('/l/?uddg=')[1].split('&')[0]
#                         link = requests.utils.unquote(decoded_url)
                    
#                     # Try to get snippet
#                     snippet = ""
#                     snippet_element = result.find_next('.result__snippet')
#                     if snippet_element:
#                         snippet = snippet_element.text.strip()
                    
#                     # Try to get date (DuckDuckGo doesn't always show dates)
#                     date = "Unknown"
#                     date_element = result.find_next(class_='result__timestamp')
#                     if date_element:
#                         date = parse_date(date_element.text.strip())
                   
#                     results.append({
#                         "title": result.text.strip(),
#                         "url": link,
#                         "source": link.split('/')[2] if '//' in link else "Unknown source",
#                         "snippet": snippet,
#                         "publish_date": date
#                     })
                   
#                     if len(results) >= max_results:
#                         break
                       
#             return results
#     except Exception as e:
#         st.error(f"DuckDuckGo search error: {e}")
#         return []

# def search_bing_news(query: str, max_results: int = 3):
#     """Search news using Bing"""
#     search_url = f"https://www.bing.com/news/search?q={query.replace(' ', '+')}"
#     headers = get_random_headers()
   
#     try:
#         with st.spinner(f"Searching Bing News for: {query}"):
#             response = requests.get(search_url, headers=headers)
#             response.raise_for_status()
           
#             soup = BeautifulSoup(response.text, 'html.parser')
#             results = []
           
#             # Extract news articles
#             for article in soup.select('.news-card'):
#                 link_element = article.select_one('a.title')
#                 if link_element:
#                     link = link_element.get('href')
#                     title = link_element.text.strip()
                   
#                     source_element = article.select_one('.source')
#                     source = source_element.text.strip() if source_element else "Unknown"
                   
#                     snippet_element = article.select_one('.snippet')
#                     snippet = snippet_element.text.strip() if snippet_element else ""
                    
#                     # Extract date from Bing News
#                     date = "Unknown"
#                     date_element = article.select_one('.time')
#                     if date_element:
#                         date = parse_date(date_element.text.strip())
                   
#                     if link and link.startswith('http'):
#                         results.append({
#                             "title": title,
#                             "url": link,
#                             "source": source,
#                             "snippet": snippet,
#                             "publish_date": date
#                         })
                       
#                         if len(results) >= max_results:
#                             break
           
#             return results
#     except Exception as e:
#         st.error(f"Bing News search error: {e}")
#         return []

# def news_api_search(query: str, max_results: int = 3, api_key: str = None):
#     """Search using NewsAPI if API key is available"""
#     if not api_key:
#         st.warning("NEWS_API_KEY not provided, skipping NewsAPI search")
#         return []
       
#     url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={api_key}"
   
#     try:
#         with st.spinner(f"Searching NewsAPI for: {query}"):
#             response = requests.get(url)
#             response.raise_for_status()
#             data = response.json()
           
#             results = []
#             if data["status"] == "ok" and data["totalResults"] > 0:
#                 for article in data["articles"][:max_results]:
#                     results.append({
#                         "title": article["title"],
#                         "url": article["url"],
#                         "source": article["source"]["name"],
#                         "snippet": article["description"] or "",
#                         "publish_date": parse_date(article.get("publishedAt", "Unknown"))
#                     })
#             return results
#     except Exception as e:
#         st.error(f"NewsAPI search error: {e}")
#         return []

# def search_raw_html(url: str, query: str, max_results: int = 3):
#     """Extract links from raw HTML of a news site"""
#     headers = get_random_headers()
   
#     try:
#         with st.spinner(f"Searching {url} for: {query}"):
#             response = requests.get(url, headers=headers)
#             response.raise_for_status()
           
#             # Find all links
#             soup = BeautifulSoup(response.text, 'html.parser')
#             results = []
           
#             # Look for links that might contain the query terms
#             query_terms = query.lower().split()
#             links = soup.find_all('a', href=True)
           
#             for link in links:
#                 href = link.get('href')
#                 text = link.text.strip()
               
#                 # Skip empty links, navigation, etc.
#                 if (not href or not text or len(text) < 15 or
#                     href.startswith('#') or 'javascript:' in href):
#                     continue
                   
#                 # Make absolute URL if needed
#                 if href.startswith('/'):
#                     href = f"{url.split('//', 1)[0]}//{url.split('//', 1)[1].split('/', 1)[0]}{href}"
#                 elif not href.startswith(('http://', 'https://')):
#                     continue
                   
#                 # Check if link text contains any query terms
#                 if any(term in text.lower() for term in query_terms):
#                     # Try to find snippet near the link
#                     snippet = ""
#                     if link.parent and link.parent.text:
#                         full_text = link.parent.text.strip()
#                         if len(full_text) > len(text):
#                             snippet = full_text
                    
#                     results.append({
#                         "title": text,
#                         "url": href,
#                         "source": href.split('/')[2] if '//' in href else "Unknown",
#                         "snippet": snippet,
#                         "publish_date": "Unknown"  # Can't get date from raw HTML
#                     })
                   
#                     if len(results) >= max_results:
#                         break
                       
#             return results
#     except Exception as e:
#         st.error(f"Raw HTML search error for {url}: {e}")
#         return []

# def multi_source_news_search(query: str, max_articles: int = 3, news_api_key: str = None) -> List[Dict]:
#     """Search multiple news sources and aggregate results"""
#     all_results = []
    
#     progress_bar = st.progress(0)
#     progress_text = st.empty()
    
#     # Try DuckDuckGo first
#     progress_text.text("Searching DuckDuckGo...")
#     results = search_duckduckgo_news(query, max_articles)
#     if results:
#         st.success(f"Found {len(results)} results from DuckDuckGo")
#         all_results.extend(results)
#     progress_bar.progress(0.25)
   
#     # If we don't have enough results, try Bing News
#     if len(all_results) < max_articles:
#         progress_text.text("Searching Bing News...")
#         remaining = max_articles - len(all_results)
#         results = search_bing_news(query, remaining)
#         if results:
#             st.success(f"Found {len(results)} results from Bing News")
#             all_results.extend(results)
#         progress_bar.progress(0.5)
   
#     # If we still don't have enough, try NewsAPI
#     if len(all_results) < max_articles and news_api_key:
#         progress_text.text("Searching NewsAPI...")
#         remaining = max_articles - len(all_results)
#         results = news_api_search(query, remaining, news_api_key)
#         if results:
#             st.success(f"Found {len(results)} results from NewsAPI")
#             all_results.extend(results)
#         progress_bar.progress(0.75)
   
#     # If still not enough, try some specific news sites directly
#     if len(all_results) < max_articles:
#         progress_text.text("Searching direct news sites...")
#         news_sites = [
#             "https://news.yahoo.com",
#             "https://www.reuters.com",
#             "https://www.bbc.com/news"
#         ]
       
#         for site in news_sites:
#             if len(all_results) >= max_articles:
#                 break
               
#             remaining = max_articles - len(all_results)
#             results = search_raw_html(site, query, remaining)
#             if results:
#                 st.success(f"Found {len(results)} results from {site}")
#                 all_results.extend(results)
    
#     progress_bar.progress(1.0)
#     progress_text.empty()
   
#     # Deduplicate by URL
#     unique_results = []
#     seen_urls = set()
   
#     for result in all_results:
#         if result["url"] not in seen_urls:
#             seen_urls.add(result["url"])
#             unique_results.append(result)
   
#     return unique_results[:max_articles]

# # Scrape individual news article
# def scrape_news_article(url: str) -> Dict:
#     with st.spinner(f"Scraping article: {url}"):
#         headers = get_random_headers()
       
#         try:
#             # First try with WebBaseLoader
#             loader = WebBaseLoader(
#                 web_paths=[url],
#                 requests_kwargs={"headers": headers}
#             )
#             document = loader.load()[0]
#             text = document.page_content.strip()
#             metadata = document.metadata
           
#             # If text is too short, try with direct requests + BeautifulSoup
#             if len(text) < 50:
#                 st.info("Content too short, trying direct parsing...")
#                 response = requests.get(url, headers=headers)
#                 response.raise_for_status()
               
#                 soup = BeautifulSoup(response.text, 'html.parser')
               
#                 # Remove script, style elements
#                 for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
#                     element.decompose()
                   
#                 # Get title
#                 title = soup.title.text.strip() if soup.title else "Untitled"
               
#                 # Extract main content
#                 article_text = ""
               
#                 # Try common article content selectors
#                 selectors = [
#                     'article', '.article', '.content', '.story', 'main',
#                     '.post-content', '.entry-content', '#content'
#                 ]
               
#                 for selector in selectors:
#                     content = soup.select_one(selector)
#                     if content:
#                         paragraphs = content.find_all('p')
#                         article_text = '\n\n'.join([p.text.strip() for p in paragraphs])
#                         if len(article_text) > 500:  # Only use if substantial content found
#                             break
                           
#                 # If still no good content, just use all paragraphs
#                 if len(article_text) < 500:
#                     paragraphs = soup.find_all('p')
#                     article_text = '\n\n'.join([p.text.strip() for p in paragraphs])
                   
#                 # Look for publish date
#                 date = None
#                 date_selectors = ['time', '.date', '.published', 'meta[property="article:published_time"]']
#                 for selector in date_selectors:
#                     date_element = soup.select_one(selector)
#                     if date_element:
#                         if date_element.name == 'meta':
#                             date = date_element.get('content', '')
#                         else:
#                             date = date_element.text.strip()
#                         break
                       
#                 return {
#                     "title": title,
#                     "text": article_text,
#                     "snippet": article_text[:200] + "..." if len(article_text) > 200 else article_text,
#                     "publish_date": parse_date(date) if date else "Unknown",
#                     "source": url.split('/')[2],
#                     "url": url
#                 }
           
#             return {
#                 "title": metadata.get("title", "Untitled"),
#                 "text": text,
#                 "snippet": text[:200] + "..." if len(text) > 200 else text,
#                 "publish_date": parse_date(metadata.get("publish_date", "Unknown")),
#                 "source": url.split('/')[2],
#                 "url": url
#             }
#         except Exception as e:
#             st.error(f"Error scraping {url}: {e}")
#             return None

# # Summarize article with fallback to snippet if text is not available
# def summarize_article(article_data: Dict, topic: str, llm, original_result: Dict = None) -> str:
#     # Check if we have article text
#     article_text = article_data.get("text", "").strip() if article_data else ""
    
#     # If article text is too short or not available, fall back to snippet from search results
#     if not article_data or len(article_text) < 100:
#         if original_result and original_result.get("snippet"):
#             st.warning("Full article text not available. Using snippet for summarization.")
#             article_text = original_result.get("snippet")
            
#             # If still no good content, cannot summarize
#             if len(article_text) < 50:
#                 return None
                
#             # Create minimal article data from snippet
#             if not article_data:
#                 article_data = {
#                     "title": original_result.get("title", "Unknown Title"),
#                     "url": original_result.get("url", ""),
#                     "source": original_result.get("source", "Unknown Source"),
#                     "publish_date": original_result.get("publish_date", "Unknown"),
#                     "text": article_text
#                 }
#         else:
#             return None
   
#     # Limit article text length to prevent token limits
#     if len(article_text) > 15000:
#         article_text = article_text[:15000] + "..."

#     with st.spinner("Generating summary..."):
#         template = """
#         Create an SEO-optimized news summary:
     
#         ARTICLE CONTENT: {article_text}
#         TITLE: {article_title}
#         PUBLISHED: {publish_date}
#         URL: {article_url}
#         TOPIC: {topic}
     
#         REQUIREMENTS:
#         - Title: Custom, SEO-optimized
#         - Length: 300-500 words
#         - Structure: Lead paragraph, context, key facts
#         - Keywords: [KEYWORDS: relevant, keywords]
#         - Include the published date prominently
     
#         OUTPUT:
#         ## [Title]
     
#         [Summary]
     
#         **Source:** [Source Name] ([article_url])
#         **Published Date:** {publish_date}
#         [KEYWORDS: keyword1, keyword2]
#         """
     
#         prompt = ChatPromptTemplate.from_template(template)
#         chain = prompt | llm | StrOutputParser()
     
#         try:
#             return chain.invoke({
#                 "article_text": article_text,
#                 "article_title": article_data["title"],
#                 "publish_date": article_data["publish_date"],
#                 "article_url": article_data["url"],
#                 "topic": topic
#             })
#         except Exception as e:
#             st.error(f"Error summarizing article: {e}")
#             return None

# def validate_groq_api_key(api_key):
#     """Validate the GROQ API key by making a simple request"""
#     if not api_key:
#         return False
    
#     try:
#         # Just initialize the client to check
#         llm = ChatGroq(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             api_key=api_key
#         )
#         return True
#     except Exception as e:
#         st.error(f"Invalid GROQ API key: {e}")
#         return False

# def validate_news_api_key(api_key):
#     """Validate the NewsAPI key by making a simple request"""
#     if not api_key:
#         # NewsAPI is optional, so we return True if not provided
#         return True
    
#     url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
#     try:
#         response = requests.get(url)
#         data = response.json()
#         if data.get("status") == "ok":
#             return True
#         else:
#             st.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
#             return False
#     except Exception as e:
#         st.error(f"Failed to validate NewsAPI key: {e}")
#         return False

# # Main Streamlit app
# def main():
#     st.title("📰 News Scraper & Summarizer")
    
#     # Sidebar for API keys
#     with st.sidebar:
#         st.header("API Keys")
        
#         # Groq API Key (required)
#         groq_api_key = st.text_input("Groq API Key (required)", 
#                                      value=st.session_state.get('groq_api_key', ''),
#                                      type="password",
#                                      help="Required for summarization. Get one from https://console.groq.com/")
        
#         # News API Key (optional)
#         news_api_key = st.text_input("News API Key (optional)", 
#                                     value=st.session_state.get('news_api_key', ''),
#                                     type="password",
#                                     help="Optional for better news search. Get one from https://newsapi.org/")
        
#         if st.button("Validate API Keys"):
#             with st.spinner("Validating API keys..."):
#                 groq_valid = validate_groq_api_key(groq_api_key)
#                 news_valid = validate_news_api_key(news_api_key)
                
#                 if groq_valid:
#                     st.session_state.groq_api_key = groq_api_key
#                     st.session_state.llm = ChatGroq(
#                         model="meta-llama/llama-4-scout-17b-16e-instruct",
#                         api_key=groq_api_key
#                     )
#                     st.success("✅ Groq API key validated!")
#                 else:
#                     st.error("❌ Invalid Groq API key!")
                
#                 if news_api_key:
#                     if news_valid:
#                         st.session_state.news_api_key = news_api_key
#                         st.success("✅ News API key validated!")
#                     else:
#                         st.error("❌ Invalid News API key!")
#                 else:
#                     st.info("No News API key provided. The app will still work but with limited sources.")
                
#                 # Set API keys valid flag
#                 st.session_state.api_keys_valid = groq_valid
        
#         st.divider()
#         st.markdown("### About")
#         st.markdown("""
#         This app:
#         1. Searches for news articles across multiple sources
#         2. Extracts the content from found articles
#         3. Uses AI to create SEO-optimized summaries
#         """)

#     # Main content area
#     if not st.session_state.api_keys_valid:
#         st.warning("Please enter and validate your Groq API key in the sidebar to continue")
#         st.stop()
    
#     # Search interface
#     st.header("Search for News")
    
#     col1, col2 = st.columns([3, 1])
#     with col1:
#         search_query = st.text_input("Enter a news topic to search", 
#                                     placeholder="e.g., climate change, technology, sports",
#                                     key="search_input",
#                                     on_change=lambda: perform_search() if st.session_state.get('search_input') else None)
    
#     with col2:
#         max_articles = st.number_input("Number of articles", min_value=1, max_value=10, value=3)
    
#     def perform_search():
#         if not st.session_state.get('search_input'):
#             st.error("Please enter a search query")
#             return
            
#         # Search for articles
#         st.session_state.search_results = multi_source_news_search(
#             st.session_state.search_input, 
#             max_articles, 
#             st.session_state.get('news_api_key')
#         )
        
#         if not st.session_state.search_results:
#             st.error("No articles found. Try another search query.")
    
#     if st.button("Search & Summarize", type="primary") or st.session_state.get('trigger_search', False):
#         st.session_state.trigger_search = False
#         perform_search()
    
#     # Display search results
#     if st.session_state.search_results:
#         st.header("Search Results")
        
#         for i, result in enumerate(st.session_state.search_results):
#             st.subheader(f"{i+1}. {result['title']}")
#             st.write(f"**Source:** {result.get('source', 'Unknown')}")
#             st.write(f"**Published:** {result.get('publish_date', 'Unknown')}")
#             st.write(f"**URL:** [{result['url']}]({result['url']})")
            
#             # Show snippet if available
#             if result.get('snippet'):
#                 with st.expander("Snippet"):
#                     st.write(result['snippet'])
            
#             # Article actions
#             if st.button("Scrape & Summarize", key=f"scrape_{i}"):
#                 # Scrape the article
#                 scraped_data = scrape_news_article(result['url'])
                
#                 # Process article data
#                 if scraped_data:
#                     # Display article details in tabs
#                     tabs = st.tabs(["Article Details", "Raw Content", "Summary"])
                    
#                     # Tab 1: Article metadata with added published date and snippet
#                     with tabs[0]:
#                         st.write(f"**Title:** {scraped_data['title']}")
#                         st.write(f"**Published:** {scraped_data['publish_date']}")
#                         st.write(f"**Source:** {scraped_data['source']}")
#                         st.write(f"**URL:** [{scraped_data['url']}]({scraped_data['url']})")
                        
#                         # Add snippet from search result if available
#                         if result.get('snippet'):
#                             st.write("**Search Snippet:**")
#                             st.write(result['snippet'])
                        
#                         # Add snippet from scraped data if available
#                         if scraped_data.get('snippet'):
#                             st.write("**Content Snippet:**")
#                             st.write(scraped_data['snippet'])
                    
#                     # Tab 2: Raw content
#                     with tabs[1]:
#                         if scraped_data.get('text') and len(scraped_data['text']) > 0:
#                             st.text_area("Content Preview", 
#                                          scraped_data['text'][:1000] + "..." if len(scraped_data['text']) > 1000 else scraped_data['text'], 
#                                          height=300)
#                         else:
#                             st.warning("No article text could be extracted.")
#                             if result.get('snippet'):
#                                 st.write("**Using search snippet instead:**")
#                                 st.write(result['snippet'])
                    
#                     # Generate summary using article text or falling back to snippet
#                     summary = summarize_article(scraped_data, search_query, st.session_state.llm, result)
                    
#                     # Tab 3: Summary
#                     with tabs[2]:
#                         if summary:
#                             st.markdown(summary)
                            
#                             # Add download button for the summary
#                             st.download_button(
#                                 label="Download Summary",
#                                 data=summary,
#                                 file_name=f"summary_{i+1}.md",
#                                 mime="text/markdown"
#                             )
#                         else:
#                             st.error("Could not generate a summary. Not enough content available.")
#                 else:
#                     st.error("Could not scrape article content.")
                    
#                     # Try to use snippet for summarization if available
#                     if result.get('snippet') and len(result['snippet']) > 50:
#                         st.warning("Attempting to summarize using search snippet only...")
                        
#                         # Create minimal article data from snippet
#                         minimal_data = {
#                             "title": result.get("title", "Unknown Title"),
#                             "url": result.get("url", ""),
#                             "source": result.get("source", "Unknown Source"),
#                             "publish_date": result.get("publish_date", "Unknown"),
#                             "text": result.get("snippet", "")
#                         }
                        
#                         summary = summarize_article(minimal_data, search_query, st.session_state.llm)
                        
#                         if summary:
#                             st.markdown("## Summary from Snippet")
#                             st.markdown(summary)
                            
#                             # Add download button for the summary
#                             st.download_button(
#                                 label="Download Summary",
#                                 data=summary,
#                                 file_name=f"summary_{i+1}.md",
#                                 mime="text/markdown"
#                             )
#                         else:
#                             st.error("Could not generate a summary from the snippet.")
            
#             # Add separator between articles
#             st.divider()

# if __name__ == "__main__":
#     main()