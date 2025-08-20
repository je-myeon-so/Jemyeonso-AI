"""
Tests for Wikipedia Service
"""
import pytest
import responses
import json
from unittest.mock import patch, Mock
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
    @responses.activate
    def test_get_concept_summary_success(self):
        """Test successful concept summary retrieval"""
        # Mock Wikipedia API response
        mock_response = {
            "title": "Python (programming language)",
            "extract": "Python is a high-level, interpreted programming language...",
            "content_urls": {
                "desktop": {
                    "page": "https://ko.wikipedia.org/wiki/Python"
                }
            }
        }
        
        responses.add(
            responses.GET,
            "https://ko.wikipedia.org/api/rest_v1/page/summary/Python",
            json=mock_response,
            status=200
        )
        
        result = self.service.get_concept_summary("Python")
        
        assert result is not None
        assert result["title"] == "Python (programming language)"
        assert "programming language" in result["extract"]
        assert "wiki/Python" in result["url"]

    @pytest.mark.unit
    @responses.activate
    def test_get_concept_summary_not_found(self):
        """Test concept summary when page not found"""
        responses.add(
            responses.GET,
            "https://ko.wikipedia.org/api/rest_v1/page/summary/NonexistentConcept",
            status=404
        )
        
        result = self.service.get_concept_summary("NonexistentConcept")
        assert result is None

    @pytest.mark.unit
    @responses.activate
    def test_get_concept_summary_timeout(self):
        """Test concept summary with timeout"""
        responses.add(
            responses.GET,
            "https://ko.wikipedia.org/api/rest_v1/page/summary/Python",
            body=responses.ConnectTimeout()
        )
        
        result = self.service.get_concept_summary("Python")
        assert result is None

    @pytest.mark.unit
    @responses.activate
    def test_get_concept_summary_invalid_json(self):
        """Test concept summary with invalid JSON response"""
        responses.add(
            responses.GET,
            "https://ko.wikipedia.org/api/rest_v1/page/summary/Python",
            body="Invalid JSON",
            status=200
        )
        
        result = self.service.get_concept_summary("Python")
        assert result is None

    @pytest.mark.unit
    @responses.activate
    def test_search_concept_success(self):
        """Test successful concept search"""
        mock_response = {
            "query": {
                "search": [
                    {"title": "Python (programming language)"}
                ]
            }
        }
        
        responses.add(
            responses.GET,
            "https://ko.wikipedia.org/w/api.php",
            json=mock_response,
            status=200
        )
        
        result = self.service.search_concept("Python programming")
        assert result == "Python (programming language)"

    @pytest.mark.unit
    @responses.activate
    def test_search_concept_no_results(self):
        """Test concept search with no results"""
        mock_response = {
            "query": {
                "search": []
            }
        }
        
        responses.add(
            responses.GET,
            "https://ko.wikipedia.org/w/api.php",
            json=mock_response,
            status=200
        )
        
        result = self.service.search_concept("NonexistentTopic")
        assert result is None

    @pytest.mark.unit
    @responses.activate
    def test_search_concept_timeout(self):
        """Test search concept with timeout"""
        responses.add(
            responses.GET,
            "https://ko.wikipedia.org/w/api.php",
            body=responses.ConnectTimeout()
        )
        
        result = self.service.search_concept("Python")
        assert result is None

    @pytest.mark.unit
    def test_caching_mechanism(self):
        """Test that caching works properly"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "title": "Python",
                "extract": "Test extract",
                "content_urls": {"desktop": {"page": "http://test.com"}}
            }
            mock_get.return_value = mock_response
            
            # First call should make HTTP request
            result1 = self.service.get_concept_summary("Python")
            
            # Second call should use cache
            result2 = self.service.get_concept_summary("Python")
            
            # Should only call requests.get once
            assert mock_get.call_count == 1
            assert result1 == result2

    @pytest.mark.unit
    def test_cache_negative_results(self):
        """Test that negative results are cached"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            # First call
            result1 = self.service.get_concept_summary("NonexistentConcept")
            
            # Second call should use cached negative result
            result2 = self.service.get_concept_summary("NonexistentConcept")
            
            assert mock_get.call_count == 1
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
    @responses.activate
    def test_url_encoding(self):
        """Test proper URL encoding for concepts with special characters"""
        concept_with_spaces = "Machine Learning"
        encoded_concept = "Machine%20Learning"
        
        responses.add(
            responses.GET,
            f"https://ko.wikipedia.org/api/rest_v1/page/summary/{encoded_concept}",
            json={"title": "Machine Learning", "extract": "Test", "content_urls": {"desktop": {"page": "test"}}},
            status=200
        )
        
        result = self.service.get_concept_summary(concept_with_spaces)
        assert result is not None
        assert result["title"] == "Machine Learning"

    @pytest.mark.unit
    @responses.activate
    def test_search_parameters(self):
        """Test that search includes correct parameters"""
        responses.add(
            responses.GET,
            "https://ko.wikipedia.org/w/api.php",
            json={"query": {"search": [{"title": "Test Result"}]}},
            status=200
        )
        
        self.service.search_concept("test query")
        
        # Verify the request was made with correct parameters
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "action=query" in request.url
        assert "list=search" in request.url
        assert "srsearch=test+query" in request.url
        assert "format=json" in request.url
        assert "srlimit=1" in request.url

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
    def test_multiple_concept_processing(self):
        """Test processing multiple concepts efficiently"""
        concepts = ["Python", "Java", "JavaScript", "C++", "Go"]
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "title": "Test Language",
                "extract": "A programming language",
                "content_urls": {"desktop": {"page": "http://test.com"}}
            }
            mock_get.return_value = mock_response
            
            results = []
            for concept in concepts:
                result = self.service.get_concept_summary(concept)
                results.append(result)
            
            # Should have made 5 requests (one per unique concept)
            assert mock_get.call_count == 5
            assert len(results) == 5
            assert all(result is not None for result in results)

    @pytest.mark.unit
    def test_error_handling_malformed_response(self):
        """Test handling of malformed API responses"""
        with patch('requests.get') as mock_get:
            # Response missing required fields
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"incomplete": "data"}
            mock_get.return_value = mock_response
            
            result = self.service.get_concept_summary("test")
            
            # Should handle gracefully and return a result with None values for missing fields
            assert result is not None
            assert result.get("title") is None
            assert result.get("extract") is None
            assert result.get("url") is None
