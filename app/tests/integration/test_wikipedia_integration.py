"""
Comprehensive integration tests for Wikipedia API functionality
"""
import pytest
import json
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestWikipediaIntegrationFlow:
    """Integration tests for complete Wikipedia API workflow"""

    @pytest.mark.integration
    @patch('app.core.wikipedia_service.WikipediaService')
    @patch('app.core.llm_utils.call_llm')
    @patch('app.interview.prompt_loader.load_prompt')
    def test_complete_analysis_with_wikipedia_context(self, mock_load_prompt, mock_call_llm, mock_wiki_service):
        """Test complete answer analysis flow with Wikipedia integration"""
        
        # Setup Wikipedia service mock
        mock_service = Mock()
        mock_wiki_service.return_value = mock_service
        
        # Mock Wikipedia responses for different concepts
        def mock_get_concept_summary(concept):
            responses = {
                "Python": {
                    "title": "Python (programming language)",
                    "extract": "Python is a high-level, interpreted programming language with dynamic semantics and simple syntax that emphasizes readability.",
                    "url": "https://ko.wikipedia.org/wiki/Python"
                },
                "Django": {
                    "title": "Django (web framework)",
                    "extract": "Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.",
                    "url": "https://ko.wikipedia.org/wiki/Django"
                },
                "REST API": {
                    "title": "REST",
                    "extract": "Representational State Transfer (REST) is a software architectural style that defines a set of constraints for web services.",
                    "url": "https://ko.wikipedia.org/wiki/REST"
                }
            }
            return responses.get(concept)
        
        mock_service.get_concept_summary.side_effect = mock_get_concept_summary
        mock_service.search_concept.return_value = None  # No search fallback needed
        
        # Setup LLM mocks
        mock_load_prompt.side_effect = [
            "Extract technical concepts from: {answer} for job type: {job_type}",
            "Analyze the following interview answer: {question} {text} {jobtype} {level} {category}"
        ]
        
        mock_call_llm.side_effect = [
            '["Python", "Django", "REST API"]',  # Concept extraction response
            json.dumps({  # Analysis response
                "score": 88,
                "feedback": "답변자는 Python, Django, REST API에 대한 정확한 이해를 보여주었습니다. 위키피디아 검증 결과 기술적 설명이 정확합니다.",
                "strengths": [
                    "Python의 특징을 정확히 설명",
                    "Django 프레임워크의 이해도 높음",
                    "REST API 개념을 명확히 파악"
                ],
                "improvements": [
                    "실제 프로젝트 경험 사례 추가",
                    "성능 최적화 관점 언급"
                ],
                "category": "우수"
            })
        ]
        
        # Make API request
        request_data = {
            "question": "Python과 Django를 사용한 REST API 개발 경험에 대해 설명해주세요.",
            "answer": "Python은 읽기 쉬운 문법을 가진 고수준 프로그래밍 언어입니다. Django는 Python 기반의 웹 프레임워크로 빠른 개발을 지원합니다. REST API는 HTTP 메서드를 활용한 웹 서비스 아키텍처 스타일입니다.",
            "jobtype": "백엔드 개발자",
            "level": "고급",
            "category": "기술"
        }
        
        response = client.post("/api/ai/analysis", json=request_data)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check analysis results
        assert data["score"] == 88
        assert "Python" in data["feedback"]
        assert "Django" in data["feedback"]
        assert "REST API" in data["feedback"]
        assert "위키피디아 검증" in data["feedback"]
        
        # Verify Wikipedia service was used for all concepts
        assert mock_service.get_concept_summary.call_count == 3
        mock_service.get_concept_summary.assert_any_call("Python")
        mock_service.get_concept_summary.assert_any_call("Django") 
        mock_service.get_concept_summary.assert_any_call("REST API")
        
        # Verify LLM was called for both concept extraction and analysis
        assert mock_call_llm.call_count == 2

    @pytest.mark.integration
    @patch('app.core.wikipedia_service.WikipediaService')
    @patch('app.core.llm_utils.call_llm')
    @patch('app.interview.prompt_loader.load_prompt')
    def test_analysis_with_wikipedia_search_fallback(self, mock_load_prompt, mock_call_llm, mock_wiki_service):
        """Test analysis flow when Wikipedia search fallback is needed"""
        
        mock_service = Mock()
        mock_wiki_service.return_value = mock_service
        
        # Mock scenario where direct lookup fails but search succeeds
        def mock_get_concept_summary(concept):
            if concept == "ML":
                return None  # Direct lookup fails
            elif concept == "Machine Learning":
                return {
                    "title": "Machine Learning",
                    "extract": "Machine learning is a method of data analysis that automates analytical model building.",
                    "url": "https://ko.wikipedia.org/wiki/Machine_Learning"
                }
            return None
        
        mock_service.get_concept_summary.side_effect = mock_get_concept_summary
        mock_service.search_concept.return_value = "Machine Learning"
        
        # Setup LLM mocks
        mock_load_prompt.side_effect = [
            "Extract concepts: {answer}",
            "Analyze: {question}"
        ]
        
        mock_call_llm.side_effect = [
            '["ML", "TensorFlow"]',  # Concept extraction with abbreviation
            json.dumps({
                "score": 82,
                "feedback": "ML에 대한 이해도가 좋습니다.",
                "strengths": ["머신러닝 기초 이해"],
                "improvements": ["구체적 예시 추가"],
                "category": "양호"
            })
        ]
        
        request_data = {
            "question": "ML 경험에 대해 말씀해주세요.",
            "answer": "ML은 데이터 분석 방법 중 하나입니다.",
            "jobtype": "데이터 사이언티스트",
            "level": "중급",
            "category": "기술"
        }
        
        response = client.post("/api/ai/analysis", json=request_data)
        
        assert response.status_code == 200
        
        # Verify search fallback was used
        mock_service.search_concept.assert_called_with("ML")
        # Should call get_concept_summary twice: once for "ML", once for "Machine Learning"
        assert mock_service.get_concept_summary.call_count >= 2

    @pytest.mark.integration
    @patch('app.core.wikipedia_service.WikipediaService')
    @patch('app.core.llm_utils.call_llm')
    def test_analysis_with_no_wikipedia_results(self, mock_call_llm, mock_wiki_service):
        """Test analysis flow when no Wikipedia results are found"""
        
        mock_service = Mock()
        mock_wiki_service.return_value = mock_service
        
        # Mock no results scenario
        mock_service.get_concept_summary.return_value = None
        mock_service.search_concept.return_value = None
        
        # Setup LLM mocks
        with patch('app.interview.prompt_loader.load_prompt') as mock_load_prompt:
            mock_load_prompt.side_effect = [
                "Extract concepts: {answer}",
                "Analyze: {question}"
            ]
            
            mock_call_llm.side_effect = [
                '["UnknownTech", "FutureTech"]',  # Non-existent concepts
                json.dumps({
                    "score": 65,
                    "feedback": "답변에서 언급한 기술들에 대한 검증이 어려웠습니다.",
                    "strengths": ["새로운 기술에 대한 관심"],
                    "improvements": ["알려진 기술 스택 활용 권장"],
                    "category": "보통"
                })
            ]
            
            request_data = {
                "question": "최신 기술 트렌드에 대해 어떻게 생각하시나요?",
                "answer": "UnknownTech와 FutureTech가 미래를 바꿀 것입니다.",
                "jobtype": "개발자",
                "level": "초급",
                "category": "기술"
            }
            
            response = client.post("/api/ai/analysis", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Should still provide analysis even without Wikipedia context
            assert "score" in data
            assert data["score"] > 0

    @pytest.mark.integration
    def test_wikipedia_caching_behavior(self):
        """Test Wikipedia service caching behavior"""
        from app.core.wikipedia_service import WikipediaService
        
        service = WikipediaService()
        
        # Clear cache initially
        service.clear_cache()
        initial_stats = service.get_cache_stats()
        assert initial_stats["concept_cache_size"] == 0
        assert initial_stats["search_cache_size"] == 0
        
        # Mock responses to test caching
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "title": "Python",
                "extract": "Test extract",
                "content_urls": {"desktop": {"page": "http://test.com"}}
            }
            mock_get.return_value = mock_response
            
            # First call should hit API
            result1 = service.get_concept_summary("Python")
            assert mock_get.call_count == 1
            
            # Second call should use cache
            result2 = service.get_concept_summary("Python")
            assert mock_get.call_count == 1  # No additional API call
            
            # Results should be identical
            assert result1 == result2
            
            # Cache stats should show 1 item
            stats = service.get_cache_stats()
            assert stats["concept_cache_size"] == 1

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_wikipedia_api_integration(self):
        """Integration test with real Wikipedia API (slow test)"""
        # This test makes actual API calls - only run when specifically testing integration
        from app.core.wikipedia_service import WikipediaService
        
        service = WikipediaService()
        
        # Test with a well-known, stable concept
        result = service.get_concept_summary("Python")
        
        if result:  # API might be down or rate limited
            assert result["title"] is not None
            assert result["extract"] is not None
            assert len(result["extract"]) > 0
            assert "python" in result["title"].lower() or "programming" in result["extract"].lower()
        else:
            pytest.skip("Wikipedia API not accessible or rate limited")
