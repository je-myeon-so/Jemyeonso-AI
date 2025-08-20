"""
Tests for Wikipedia Service using hybrid approach (wikipedia + wikipedia-api packages)
"""
import pytest
from unittest.mock import patch, Mock
import wikipedia
from app.core.wikipedia_service import WikipediaService


class TestWikipediaService:
    """Test cases for WikipediaService class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.service = WikipediaService()

    def teardown_method(self):
        """Cleanup after each test"""
        self.service.clear_cache()

    @pytest.mark.unit
    def test_get_concept_summary_success(self):
        """Test successful concept summary retrieval"""
        with patch.object(self.service.wiki_api, 'page') as mock_page:
            # Create mock page object
            mock_page_obj = Mock()
            mock_page_obj.exists.return_value = True
            mock_page_obj.title = "Python (programming language)"
            mock_page_obj.summary = "Python is a high-level, interpreted programming language with dynamic semantics."
            mock_page_obj.fullurl = "https://ko.wikipedia.org/wiki/Python_(programming_language)"
            mock_page.return_value = mock_page_obj
            
            result = self.service.get_concept_summary("Python")
            
            assert result is not None
            assert result["title"] == "Python (programming language)"
            assert "programming language" in result["extract"]
            assert "wiki/Python" in result["url"]
            mock_page.assert_called_once_with("Python")

    @pytest.mark.unit
    def test_get_concept_summary_not_found_direct(self):
        """Test concept summary when page not found directly"""
        with patch.object(self.service.wiki_api, 'page') as mock_page, \
             patch.object(self.service, 'search_concept') as mock_search:
            
            # First page lookup fails
            mock_page_obj = Mock()
            mock_page_obj.exists.return_value = False
            mock_page.return_value = mock_page_obj
            
            # Search also returns None
            mock_search.return_value = None
            
            result = self.service.get_concept_summary("NonexistentConcept")
            assert result is None
            mock_search.assert_called_once_with("NonexistentConcept")

    @pytest.mark.unit
    def test_get_concept_summary_found_via_search(self):
        """Test concept summary found via search when direct lookup fails"""
        with patch.object(self.service.wiki_api, 'page') as mock_page, \
             patch.object(self.service, 'search_concept') as mock_search:
            
            # First call (direct lookup) - page doesn't exist
            mock_page_obj_1 = Mock()
            mock_page_obj_1.exists.return_value = False
            
            # Second call (after search) - page exists
            mock_page_obj_2 = Mock()
            mock_page_obj_2.exists.return_value = True
            mock_page_obj_2.title = "Python (programming language)"
            mock_page_obj_2.summary = "Python is a programming language."
            mock_page_obj_2.fullurl = "https://ko.wikipedia.org/wiki/Python_(programming_language)"
            
            mock_page.side_effect = [mock_page_obj_1, mock_page_obj_2]
            mock_search.return_value = "Python (programming language)"
            
            result = self.service.get_concept_summary("Python programming")
            
            assert result is not None
            assert result["title"] == "Python (programming language)"
            assert mock_page.call_count == 2
            mock_search.assert_called_once_with("Python programming")

    @pytest.mark.unit
    def test_get_concept_summary_exception(self):
        """Test concept summary with exception"""
        with patch.object(self.service.wiki_api, 'page') as mock_page:
            mock_page.side_effect = Exception("API Error")
            
            result = self.service.get_concept_summary("Python")
            assert result is None

    @pytest.mark.unit
    def test_get_concept_summary_long_text_truncation(self):
        """Test that long summaries are properly truncated"""
        with patch.object(self.service.wiki_api, 'page') as mock_page:
            # Create mock page with very long summary
            long_summary = "This is a very long summary. " * 50  # Much longer than 500 chars
            
            mock_page_obj = Mock()
            mock_page_obj.exists.return_value = True
            mock_page_obj.title = "Long Article"
            mock_page_obj.summary = long_summary
            mock_page_obj.fullurl = "https://ko.wikipedia.org/wiki/Long_Article"
            mock_page.return_value = mock_page_obj
            
            result = self.service.get_concept_summary("Long Article")
            
            assert result is not None
            assert len(result["extract"]) <= 505  # 500 + "..." or sentence boundary
            assert result["extract"].endswith('.') or result["extract"].endswith('...')

    @pytest.mark.unit
    @patch('wikipedia.search')
    def test_search_concept_success(self, mock_search):
        """Test successful concept search using wikipedia package"""
        mock_search.return_value = ["Python (programming language)"]
        
        result = self.service.search_concept("Python programming")
        
        assert result == "Python (programming language)"
        mock_search.assert_called_once_with("Python programming", results=1)

    @pytest.mark.unit
    @patch('wikipedia.search')
    def test_search_concept_no_results(self, mock_search):
        """Test concept search with no results"""
        mock_search.return_value = []
        
        result = self.service.search_concept("NonexistentTopic")
        assert result is None

    @pytest.mark.unit
    @patch('wikipedia.search')
    def test_search_concept_exception(self, mock_search):
        """Test search concept with exception"""
        mock_search.side_effect = Exception("Search Error")
        
        result = self.service.search_concept("Python")
        assert result is None

    @pytest.mark.unit
    def test_get_page_content_success(self):
        """Test successful page content retrieval using wikipedia-api"""
        with patch.object(self.service.wiki_api, 'page') as mock_page:
            mock_page_obj = Mock()
            mock_page_obj.exists.return_value = True
            mock_page_obj.text = "Full page content here..."
            mock_page.return_value = mock_page_obj
            
            result = self.service.get_page_content("Python")
            
            assert result == "Full page content here..."
            mock_page.assert_called_once_with("Python")

    @pytest.mark.unit
    def test_get_page_content_not_found(self):
        """Test page content when page doesn't exist"""
        with patch.object(self.service.wiki_api, 'page') as mock_page:
            mock_page_obj = Mock()
            mock_page_obj.exists.return_value = False
            mock_page.return_value = mock_page_obj
            
            result = self.service.get_page_content("NonexistentPage")
            assert result is None

    @pytest.mark.unit
    def test_get_page_sections_success(self):
        """Test successful page sections retrieval using wikipedia-api"""
        with patch.object(self.service.wiki_api, 'page') as mock_page:
            # Create mock sections
            mock_section1 = Mock()
            mock_section1.title = "Introduction"
            mock_section1.text = "Intro text here"
            
            mock_section2 = Mock()
            mock_section2.title = "History"
            mock_section2.text = "History text here"
            
            mock_page_obj = Mock()
            mock_page_obj.exists.return_value = True
            mock_page_obj.sections = [mock_section1, mock_section2]
            mock_page.return_value = mock_page_obj
            
            result = self.service.get_page_sections("Python")
            
            assert result is not None
            assert len(result) == 2
            assert result["Introduction"] == "Intro text here"
            assert result["History"] == "History text here"

    @pytest.mark.unit
    @patch('wikipedia.summary')
    def test_get_page_summary_success(self, mock_summary):
        """Test successful page summary retrieval using wikipedia package"""
        mock_summary.return_value = "Python is a programming language. It was created by Guido van Rossum. It is widely used."
        
        result = self.service.get_page_summary("Python", sentences=3)
        
        assert result is not None
        assert "programming language" in result
        mock_summary.assert_called_once_with("Python", sentences=3)

    @pytest.mark.unit
    @patch('wikipedia.summary')
    def test_get_page_summary_disambiguation(self, mock_summary):
        """Test page summary with disambiguation error"""
        disambiguation_error = wikipedia.DisambiguationError("Python", ["Python (programming language)", "Python (snake)"])
        mock_summary.side_effect = [
            disambiguation_error,
            "Python is a programming language created by Guido van Rossum."
        ]
        
        result = self.service.get_page_summary("Python", sentences=2)
        
        assert result is not None
        assert "programming language" in result
        assert mock_summary.call_count == 2
        mock_summary.assert_any_call("Python", sentences=2)
        mock_summary.assert_any_call("Python (programming language)", sentences=2)

    @pytest.mark.unit
    @patch('wikipedia.suggest')
    def test_suggest_success(self, mock_suggest):
        """Test successful suggestion retrieval using wikipedia package"""
        mock_suggest.return_value = "python"
        
        result = self.service.suggest("pythn")
        
        assert result == "python"
        mock_suggest.assert_called_once_with("pythn")

    @pytest.mark.unit
    @patch('wikipedia.suggest')
    def test_suggest_no_suggestion(self, mock_suggest):
        """Test suggestion when no suggestion available"""
        mock_suggest.return_value = None
        
        result = self.service.suggest("validword")
        assert result is None

    @pytest.mark.unit
    def test_get_page_categories_success(self):
        """Test successful page categories retrieval using wikipedia-api"""
        with patch.object(self.service.wiki_api, 'page') as mock_page:
            mock_page_obj = Mock()
            mock_page_obj.exists.return_value = True
            mock_page_obj.categories = {
                "Programming languages": Mock(),
                "Python (programming language)": Mock(),
                "Object-oriented programming languages": Mock()
            }
            mock_page.return_value = mock_page_obj
            
            result = self.service.get_page_categories("Python")
            
            assert result is not None
            assert len(result) == 3
            assert "Programming languages" in result
            assert "Python (programming language)" in result

    @pytest.mark.unit
    def test_get_page_links_success(self):
        """Test successful page links retrieval using wikipedia-api"""
        with patch.object(self.service.wiki_api, 'page') as mock_page:
            mock_page_obj = Mock()
            mock_page_obj.exists.return_value = True
            mock_page_obj.links = {
                "Guido van Rossum": Mock(),
                "Programming language": Mock(),
                "Object-oriented programming": Mock()
            }
            mock_page.return_value = mock_page_obj
            
            result = self.service.get_page_links("Python")
            
            assert result is not None
            assert len(result) == 3
            assert "Guido van Rossum" in result
            assert "Programming language" in result

    @pytest.mark.unit
    def test_caching_mechanism(self):
        """Test that caching works properly"""
        with patch.object(self.service.wiki_api, 'page') as mock_page:
            mock_page_obj = Mock()
            mock_page_obj.exists.return_value = True
            mock_page_obj.title = "Python"
            mock_page_obj.summary = "Test extract"
            mock_page_obj.fullurl = "http://test.com"
            mock_page.return_value = mock_page_obj
            
            # First call should query Wikipedia
            result1 = self.service.get_concept_summary("Python")
            
            # Second call should use cache
            result2 = self.service.get_concept_summary("Python")
            
            # Should only call wiki_api.page once
            assert mock_page.call_count == 1
            assert result1 == result2

    @pytest.mark.unit
    def test_cache_negative_results(self):
        """Test that negative results are cached"""
        with patch.object(self.service.wiki_api, 'page') as mock_page, \
             patch.object(self.service, 'search_concept') as mock_search:
            
            mock_page_obj = Mock()
            mock_page_obj.exists.return_value = False
            mock_page.return_value = mock_page_obj
            mock_search.return_value = None
            
            # First call
            result1 = self.service.get_concept_summary("NonexistentConcept")
            
            # Second call should use cached negative result
            result2 = self.service.get_concept_summary("NonexistentConcept")
            
            # Should only call wiki_api.page and search once
            assert mock_page.call_count == 1
            assert mock_search.call_count == 1
            assert result1 is None
            assert result2 is None

    @pytest.mark.unit
    def test_clear_cache(self):
        """Test cache clearing functionality"""
        # Add some data to cache
        self.service._concept_cache["test"] = {"title": "test"}
        self.service._search_cache["test"] = "test result"
        
        # Verify data is in cache
        assert len(self.service._concept_cache) == 1
        assert len(self.service._search_cache) == 1
        
        # Clear cache
        self.service.clear_cache()
        
        # Verify cache is empty
        assert len(self.service._concept_cache) == 0
        assert len(self.service._search_cache) == 0

    @pytest.mark.unit
    def test_get_cache_stats(self):
        """Test cache statistics functionality"""
        # Initially empty
        stats = self.service.get_cache_stats()
        assert stats["concept_cache_size"] == 0
        assert stats["search_cache_size"] == 0
        
        # Add some test data
        self.service._concept_cache["test1"] = {"title": "test1"}
        self.service._concept_cache["test2"] = {"title": "test2"}
        self.service._search_cache["search1"] = "result1"
        
        # Check updated stats
        stats = self.service.get_cache_stats()
        assert stats["concept_cache_size"] == 2
        assert stats["search_cache_size"] == 1

    @pytest.mark.unit
    @patch('wikipedia.set_lang')
    def test_set_language(self, mock_set_lang):
        """Test language setting functionality"""
        original_wiki_api = self.service.wiki_api
        
        # Change to English
        self.service.set_language("en")
        
        # Should call wikipedia.set_lang
        mock_set_lang.assert_called_with("en")
        assert self.service.language == "en"
        
        # Should create new wikipedia-api instance
        assert self.service.wiki_api != original_wiki_api
        
        # Cache should be cleared
        assert len(self.service._concept_cache) == 0
        assert len(self.service._search_cache) == 0

    @pytest.mark.unit
    @patch('wikipedia.set_lang')
    def test_initialization_with_custom_language(self, mock_set_lang):
        """Test service initialization with custom language"""
        service = WikipediaService(language="en")
        
        # Should initialize with English Wikipedia
        mock_set_lang.assert_called_with("en")
        assert service.language == "en"
        assert service.wiki_api.language == "en"

    @pytest.mark.unit
    @patch('wikipedia.languages')
    def test_get_supported_languages(self, mock_languages):
        """Test getting supported languages"""
        mock_languages.return_value = {"en": "English", "ko": "Korean", "ja": "Japanese"}
        
        result = self.service.get_supported_languages()
        
        assert result == ["en", "ko", "ja"]
        mock_languages.assert_called_once()

    @pytest.mark.unit
    @patch('wikipedia.languages')
    def test_get_supported_languages_exception(self, mock_languages):
        """Test getting supported languages with exception"""
        mock_languages.side_effect = Exception("API Error")
        
        result = self.service.get_supported_languages()
        
        # Should return fallback languages
        assert "en" in result
        assert "ko" in result
        assert len(result) >= 5  # Should have common languages

    @pytest.mark.unit
    @patch('wikipedia.search')
    def test_search_cache_functionality(self, mock_search):
        """Test that search results are properly cached"""
        mock_search.return_value = ["Python (programming language)"]
        
        # First call
        result1 = self.service.search_concept("Python programming")
        
        # Second call should use cache
        result2 = self.service.search_concept("Python programming")
        
        # Should only call search once
        assert mock_search.call_count == 1
        assert result1 == result2 == "Python (programming language)"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_api_call(self):
        """Integration test with real Wikipedia API (marked as slow)"""
        # This test makes actual API calls, so it's marked as slow
        # Run with: pytest -m "not slow" to skip in regular testing
        service = WikipediaService()
        
        # Test with a well-known concept
        result = service.get_concept_summary("Python")
        
        if result:  # API might be down or blocked
            assert "title" in result
            assert "extract" in result
            assert result["extract"] is not None

    @pytest.mark.unit
    def test_hybrid_approach_benefits(self):
        """Test that hybrid approach uses both packages appropriately"""
        with patch('wikipedia.search') as mock_search, \
             patch.object(self.service.wiki_api, 'page') as mock_page:
            
            # Setup mocks
            mock_search.return_value = ["Python (programming language)"]
            
            mock_page_obj = Mock()
            mock_page_obj.exists.return_value = True
            mock_page_obj.title = "Python (programming language)"
            mock_page_obj.summary = "Python is a programming language."
            mock_page_obj.fullurl = "https://ko.wikipedia.org/wiki/Python"
            mock_page.return_value = mock_page_obj
            
            # Test search functionality (uses wikipedia package)
            search_result = self.service.search_concept("Python programming")
            assert search_result == "Python (programming language)"
            mock_search.assert_called_once()
            
            # Test content retrieval (uses wikipedia-api package)  
            content_result = self.service.get_concept_summary("Python")
            assert content_result["title"] == "Python (programming language)"
            mock_page.assert_called_once()
