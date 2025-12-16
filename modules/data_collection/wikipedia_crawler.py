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
        """Crawl single Wikipedia article by title using API"""
        try:
            # Use Wikipedia API to get article content
            params = {
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "extracts",
                "explaintext": True,  # Get plain text instead of HTML
                "exsectionformat": "plain"
            }

            response = self.session.get(self.API_URL, params=params)

            if response.status_code != 200:
                return None

            data = response.json()
            pages = data.get('query', {}).get('pages', {})

            if not pages:
                return None

            # Get first page (should be only one)
            page_id = list(pages.keys())[0]
            page = pages[page_id]

            # Check if page exists
            if page_id == '-1' or 'missing' in page:
                return None

            # Extract content
            content = page.get('extract', '')
            display_title = page.get('title', title)

            if not content or len(content) < 100:
                return None

            url = self.BASE_URL + urllib.parse.quote(title.replace(' ', '_'))

            return {
                'title': display_title,
                'slug': title.replace(' ', '_'),
                'url': url,
                'content': content
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
            return [result['title'] for result in data.get('query', {}).get('search', [])]
        except Exception as e:
            print(f"Error searching {query}: {e}")
            return []

    def get_category_members(self, category: str, limit: int = 100) -> list:
        """Get all articles in a Wikipedia category"""
        try:
            members = []
            continue_token = None

            while len(members) < limit:
                params = {
                    "action": "query",
                    "format": "json",
                    "list": "categorymembers",
                    "cmtitle": f"Category:{category}" if not category.startswith("Category:") else category,
                    "cmlimit": min(500, limit - len(members)),
                    "cmtype": "page",  # Only pages, not subcategories
                    "cmnamespace": "0"  # Main namespace only
                }

                if continue_token:
                    params['cmcontinue'] = continue_token

                response = self.session.get(self.API_URL, params=params)
                data = response.json()

                category_members = data.get('query', {}).get('categorymembers', [])
                members.extend([member['title'] for member in category_members])

                # Check if there's more
                if 'continue' in data and len(members) < limit:
                    continue_token = data['continue'].get('cmcontinue')
                else:
                    break

            return members[:limit]

        except Exception as e:
            print(f"Error getting category members for {category}: {e}")
            return []
