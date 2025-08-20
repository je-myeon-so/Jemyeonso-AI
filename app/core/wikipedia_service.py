import wikipedia
import wikipediaapi
from typing import Optional, Dict, List
import logging

logging.getLogger("wikipedia").setLevel(logging.WARNING)


class WikipediaService:
    def __init__(self, language: str = "ko"):
        self.language = language
        
        wikipedia.set_lang(language)
        
        self.wiki_api = wikipediaapi.Wikipedia(
            language=language,
            user_agent='InterviewBot/1.0 (https://example.com/contact)'
        )
        
        self._concept_cache: Dict[str, Optional[Dict]] = {}
        self._search_cache: Dict[str, Optional[str]] = {}

    def get_concept_summary(self, concept: str) -> Optional[Dict]:
        if concept in self._concept_cache:
            return self._concept_cache[concept]
        
        try:
            page = self.wiki_api.page(concept)
            
            if not page.exists():
                search_result = self.search_concept(concept)
                if search_result:
                    page = self.wiki_api.page(search_result)
                    
            if page.exists():
                # Extract summary (first paragraph or up to 500 characters)
                summary_text = page.summary
                if len(summary_text) > 500:
                    truncated = summary_text[:500]
                    last_period = truncated.rfind('.')
                    if last_period > 200:  # Ensure we have substantial content
                        summary_text = truncated[:last_period + 1]
                    else:
                        summary_text = truncated + "..."
                
                result = {
                    "title": page.title,
                    "extract": summary_text,
                    "url": page.fullurl
                }
                
                self._concept_cache[concept] = result
                return result
            else:
                self._concept_cache[concept] = None
                return None
                
        except Exception as e:
            print(f"Wikipedia API error for concept '{concept}': {e}")
            self._concept_cache[concept] = None
            return None

    def search_concept(self, query: str) -> Optional[str]:
        if query in self._search_cache:
            return self._search_cache[query]
        
        try:
            search_results = wikipedia.search(query, results=1)
            
            if search_results:
                result = search_results[0]
                self._search_cache[query] = result
                return result
            else:
                self._search_cache[query] = None
                return None
                
        except Exception as e:
            print(f"Wikipedia search error for query '{query}': {e}")
            self._search_cache[query] = None
            return None
    
    def get_page_content(self, title: str) -> Optional[str]:
        try:
            page = self.wiki_api.page(title)
            if page.exists():
                return page.text
            return None
        except Exception as e:
            print(f"Wikipedia content error for title '{title}': {e}")
            return None
    
    def get_page_sections(self, title: str) -> Optional[Dict[str, str]]:
        try:
            page = self.wiki_api.page(title)
            if page.exists():
                sections = {}
                for section in page.sections:
                    sections[section.title] = section.text
                return sections
            return None
        except Exception as e:
            print(f"Wikipedia sections error for title '{title}': {e}")
            return None

    def get_page_summary(self, title: str, sentences: int = 3) -> Optional[str]:
        try:
            summary = wikipedia.summary(title, sentences=sentences)
            return summary
        except (wikipedia.PageError, wikipedia.DisambiguationError) as e:
            if isinstance(e, wikipedia.DisambiguationError) and e.options:
                try:
                    summary = wikipedia.summary(e.options[0], sentences=sentences)
                    return summary
                except (wikipedia.PageError, wikipedia.DisambiguationError):
                    return None
            return None
        except Exception as e:
            print(f"Wikipedia summary error for title '{title}': {e}")
            return None

    def suggest(self, query: str) -> Optional[str]:
        try:
            suggestion = wikipedia.suggest(query)
            return suggestion
        except Exception as e:
            print(f"Wikipedia suggest error for query '{query}': {e}")
            return None

    def get_page_categories(self, title: str) -> Optional[List[str]]:
        try:
            page = self.wiki_api.page(title)
            if page.exists():
                return list(page.categories.keys())
            return None
        except Exception as e:
            print(f"Wikipedia categories error for title '{title}': {e}")
            return None

    def get_page_links(self, title: str) -> Optional[List[str]]:
        try:
            page = self.wiki_api.page(title)
            if page.exists():
                return list(page.links.keys())
            return None
        except Exception as e:
            print(f"Wikipedia links error for title '{title}': {e}")
            return None
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._concept_cache.clear()
        self._search_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        return {
            "concept_cache_size": len(self._concept_cache),
            "search_cache_size": len(self._search_cache)
        }

    def set_language(self, language: str) -> None:
        self.language = language
        
        wikipedia.set_lang(language)

        self.wiki_api = wikipediaapi.Wikipedia(
            language=language,
            user_agent='InterviewBot/1.0 (https://example.com/contact)'
        )
        
        self.clear_cache()

    def get_supported_languages(self) -> List[str]:
        try:
            return list(wikipedia.languages().keys())
        except Exception as e:
            print(f"Error getting supported languages: {e}")
            return ["en", "ko", "ja", "de", "fr", "es", "it", "ru", "zh"]  # Common fallback
