import requests
import urllib.parse
from typing import Optional, Dict


class WikipediaService:
    def __init__(self):
        self.base_url = "https://ko.wikipedia.org/api/rest_v1/page/summary"
        self.search_url = "https://ko.wikipedia.org/w/api.php"

    def get_concept_summary(self, concept: str) -> Optional[Dict]:
        try:
            encoded_concept = urllib.parse.quote(concept, safe='')
            response = requests.get(f"{self.base_url}/{encoded_concept}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "title": data.get("title"),
                    "extract": data.get("extract"),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page")
                }
        except:
            return None

    def search_concept(self, query: str) -> Optional[str]:
        try:
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 1
            }
            response = requests.get(self.search_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data["query"]["search"]:
                    return data["query"]["search"][0]["title"]
        except:
            return None
