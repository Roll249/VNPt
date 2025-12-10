import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse

class VietnameseWikiCrawler:
    BASE_URL = "https://vi.wikipedia.org/wiki/"
    API_URL = "https://vi.wikipedia.org/w/api.php"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "VNPT-AI-Hackathon-Bot/1.0 (Student Project; contact@example.com)"
        })

    def crawl_article(self, title: str) -> dict:
        """Crawl single Wikipedia article by title (part after /wiki/)"""
        url = self.BASE_URL + urllib.parse.quote(title)
        
        try:
            response = self.session.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch {title}: {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title (heading)
            heading = soup.find('h1', {'id': 'firstHeading'})
            display_title = heading.get_text() if heading else title

            # Extract main content
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if not content_div:
                return None
                
            # Remove unwanted elements (tables, references, edit links)
            for tag in content_div.find_all(['table', 'div', 'sup', 'style', 'script']):
                # Keep some divs if they are just structual, but remove boxes. 
                # Simplest is to remove 'infobox', 'navbox', 'reflist'
                classes = tag.get('class', [])
                if any(c in classes for c in ['infobox', 'navbox', 'reflist', 'reference']):
                    tag.decompose()

            paragraphs = content_div.find_all('p')
            text_content = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text:
                    text_content.append(text)
            
            full_text = '\n\n'.join(text_content)

            return {
                'title': display_title,
                'slug': title,
                'url': url,
                'content': full_text
            }

        except Exception as e:
            print(f"Error crawling {title}: {e}")
            return None

    def search_related(self, query: str, limit: int = 5) -> list:
        """Search for articles related to a query"""
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": limit
        }
        try:
            response = self.session.get(self.API_URL, params=params)
            data = response.json()
            return [result['title'].replace(' ', '_') for result in data.get('query', {}).get('search', [])]
        except Exception as e:
            print(f"Error searching {query}: {e}")
            return []
