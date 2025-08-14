import requests
import urllib.parse
from typing import Optional, Dict
from functools import lru_cache


class WikipediaService:
    def __init__(self):
        self.base_url = "https://ko.wikipedia.org/api/rest_v1/page/summary"
        self.search_url = "https://ko.wikipedia.org/w/api.php"
        # In-memory cache for concept summaries
        self._concept_cache: Dict[str, Optional[Dict]] = {}
        self._search_cache: Dict[str, Optional[str]] = {}

    def get_concept_summary(self, concept: str) -> Optional[Dict]:
        # Check cache first
        if concept in self._concept_cache:
            return self._concept_cache[concept]
        
        try:
            encoded_concept = urllib.parse.quote(concept, safe='')
            response = requests.get(f"{self.base_url}/{encoded_concept}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                result = {
                    "title": data.get("title"),
                    "extract": data.get("extract"),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page")
                }
                # Cache the result
                self._concept_cache[concept] = result
                return result
        except (requests.RequestException, requests.Timeout, ValueError, KeyError):
            # Cache negative results to avoid repeated failed requests
            self._concept_cache[concept] = None
            return None

    def search_concept(self, query: str) -> Optional[str]:
        # Check cache first
        if query in self._search_cache:
            return self._search_cache[query]
        
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
                    result = data["query"]["search"][0]["title"]
                    # Cache the result
                    self._search_cache[query] = result
                    return result
        except (requests.RequestException, requests.Timeout, ValueError, KeyError):
            # Cache negative results
            self._search_cache[query] = None
            return None
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._concept_cache.clear()
        self._search_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics for monitoring"""
        return {
            "concept_cache_size": len(self._concept_cache),
            "search_cache_size": len(self._search_cache)
        }
