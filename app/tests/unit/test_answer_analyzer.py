"""
Tests for Answer Analyzer
"""
import pytest
import json
from unittest.mock import patch, Mock, MagicMock
from app.interview.answer_analyzer import (
    extract_technical_concepts,
    get_wikipedia_context,
    analyze_answer,
    MAX_CONCEPTS_TO_PROCESS,
    WIKIPEDIA_EXTRACT_TRUNCATE_LENGTH
)


class TestExtractTechnicalConcepts:
    """Test cases for extract_technical_concepts function"""

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.load_prompt')
    @patch('app.interview.answer_analyzer.call_llm')
    def test_extract_technical_concepts_success(self, mock_call_llm, mock_load_prompt):
        """Test successful technical concept extraction"""
        mock_load_prompt.return_value = "Extract concepts from {answer} for {job_type}"
        mock_call_llm.return_value = '["Python", "Django", "REST API"]'
        
        result = extract_technical_concepts("I use Python and Django for REST APIs", "Backend Developer")
        
        assert result == ["Python", "Django", "REST API"]
        mock_load_prompt.assert_called_once_with("concept_extraction.txt")
        mock_call_llm.assert_called_once()

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.load_prompt')
    def test_extract_technical_concepts_prompt_not_found(self, mock_load_prompt):
        """Test handling when prompt file is not found"""
        mock_load_prompt.side_effect = FileNotFoundError()
        
        result = extract_technical_concepts("test answer", "Developer")
        
        assert result == []

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.load_prompt')
    @patch('app.interview.answer_analyzer.call_llm')
    def test_extract_technical_concepts_invalid_json(self, mock_call_llm, mock_load_prompt):
        """Test handling of invalid JSON response"""
        mock_load_prompt.return_value = "template"
        mock_call_llm.return_value = "Invalid JSON response"
        
        result = extract_technical_concepts("test answer", "Developer")
        
        assert result == []

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.load_prompt')
    @patch('app.interview.answer_analyzer.call_llm')
    def test_extract_technical_concepts_non_list_response(self, mock_call_llm, mock_load_prompt):
        """Test handling when LLM returns non-list JSON"""
        mock_load_prompt.return_value = "template"
        mock_call_llm.return_value = '{"not": "a list"}'
        
        result = extract_technical_concepts("test answer", "Developer")
        
        assert result == []

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.load_prompt')
    @patch('app.interview.answer_analyzer.call_llm')
    def test_extract_technical_concepts_llm_exception(self, mock_call_llm, mock_load_prompt):
        """Test handling of LLM call exceptions"""
        mock_load_prompt.return_value = "template"
        mock_call_llm.side_effect = Exception("LLM error")
        
        result = extract_technical_concepts("test answer", "Developer")
        
        assert result == []


class TestGetWikipediaContext:
    """Test cases for get_wikipedia_context function"""

    @pytest.mark.unit
    def test_get_wikipedia_context_empty_concepts(self):
        """Test with empty concepts list"""
        result = get_wikipedia_context([])
        
        assert result == ""

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.WikipediaService')
    def test_get_wikipedia_context_success(self, mock_wiki_service_class):
        """Test successful Wikipedia context generation"""
        mock_service = Mock()
        mock_wiki_service_class.return_value = mock_service
        
        # Mock successful concept summary
        mock_service.get_concept_summary.return_value = {
            "title": "Python",
            "extract": "Python is a high-level programming language" * 10,  # Long extract
            "url": "https://ko.wikipedia.org/wiki/Python"
        }
        
        concepts = ["Python", "Django"]
        result = get_wikipedia_context(concepts)
        
        assert "기술적 정확성 검증을 위한 참고 정보" in result
        assert "Python" in result
        assert len(result) > 100  # Should contain substantial content

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.WikipediaService')
    def test_get_wikipedia_context_with_search_fallback(self, mock_wiki_service_class):
        """Test Wikipedia context with search fallback"""
        mock_service = Mock()
        mock_wiki_service_class.return_value = mock_service
        
        # First call returns None, second call (after search) returns data
        mock_service.get_concept_summary.side_effect = [
            None,  # First direct lookup fails
            {
                "title": "Machine Learning",
                "extract": "Machine learning is a method of data analysis",
                "url": "https://ko.wikipedia.org/wiki/Machine_Learning"
            }
        ]
        mock_service.search_concept.return_value = "Machine Learning"
        
        result = get_wikipedia_context(["ML"])
        
        assert "Machine learning" in result
        assert mock_service.search_concept.called

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.WikipediaService')
    def test_get_wikipedia_context_no_results(self, mock_wiki_service_class):
        """Test when no Wikipedia results are found"""
        mock_service = Mock()
        mock_wiki_service_class.return_value = mock_service
        
        mock_service.get_concept_summary.return_value = None
        mock_service.search_concept.return_value = None
        
        result = get_wikipedia_context(["UnknownConcept"])
        
        # Should still return the header but no concept details
        assert "기술적 정확성 검증을 위한 참고 정보" in result
        assert "UnknownConcept" not in result

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.WikipediaService')
    def test_get_wikipedia_context_max_concepts_limit(self, mock_wiki_service_class):
        """Test that only MAX_CONCEPTS_TO_PROCESS concepts are processed"""
        mock_service = Mock()
        mock_wiki_service_class.return_value = mock_service
        
        mock_service.get_concept_summary.return_value = {
            "title": "Test",
            "extract": "Test extract",
            "url": "https://test.com"
        }
        
        # Provide more concepts than the limit
        many_concepts = [f"Concept{i}" for i in range(MAX_CONCEPTS_TO_PROCESS + 2)]
        get_wikipedia_context(many_concepts)
        
        # Should only call get_concept_summary for MAX_CONCEPTS_TO_PROCESS
        assert mock_service.get_concept_summary.call_count == MAX_CONCEPTS_TO_PROCESS

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.WikipediaService')
    def test_get_wikipedia_context_extract_truncation(self, mock_wiki_service_class):
        """Test that long extracts are properly truncated"""
        mock_service = Mock()
        mock_wiki_service_class.return_value = mock_service
        
        long_extract = "A" * (WIKIPEDIA_EXTRACT_TRUNCATE_LENGTH + 100)
        mock_service.get_concept_summary.return_value = {
            "title": "LongConcept",
            "extract": long_extract,
            "url": "https://test.com"
        }
        
        result = get_wikipedia_context(["LongConcept"])
        
        # Extract should be truncated
        assert "A" * WIKIPEDIA_EXTRACT_TRUNCATE_LENGTH in result
        assert len(result) < len(long_extract) + 200  # Much shorter than original


class TestAnalyzeAnswer:
    """Test cases for analyze_answer function"""

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.extract_technical_concepts')
    @patch('app.interview.answer_analyzer.get_wikipedia_context')
    @patch('app.interview.answer_analyzer.load_prompt')
    @patch('app.interview.answer_analyzer.call_llm')
    def test_analyze_answer_success(self, mock_call_llm, mock_load_prompt, 
                                  mock_get_wiki_context, mock_extract_concepts):
        """Test successful answer analysis"""
        mock_extract_concepts.return_value = ["Python", "Django"]
        mock_get_wiki_context.return_value = "Wiki context"
        mock_load_prompt.return_value = "Analysis template: {question} {text} {jobtype} {level} {category}"
        
        mock_analysis_result = {
            "score": 85,
            "feedback": "Good technical explanation",
            "strengths": ["Clear explanation", "Good examples"],
            "improvements": ["Could add more details"]
        }
        mock_call_llm.return_value = json.dumps(mock_analysis_result)
        
        result = analyze_answer(
            question="What is Python?",
            answer="Python is a programming language...",
            jobtype="Backend Developer",
            level="Junior",
            category="Technical"
        )
        
        assert result == mock_analysis_result
        mock_extract_concepts.assert_called_once()
        mock_get_wiki_context.assert_called_once()
        mock_call_llm.assert_called_once()

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.extract_technical_concepts')
    @patch('app.interview.answer_analyzer.get_wikipedia_context')
    @patch('app.interview.answer_analyzer.load_prompt')
    @patch('app.interview.answer_analyzer.call_llm')
    def test_analyze_answer_llm_exception(self, mock_call_llm, mock_load_prompt,
                                        mock_get_wiki_context, mock_extract_concepts):
        """Test handling of LLM exceptions"""
        mock_extract_concepts.return_value = ["Python"]
        mock_get_wiki_context.return_value = "Wiki context"
        mock_load_prompt.return_value = "template"
        mock_call_llm.side_effect = ConnectionError("Network error")
        
        result = analyze_answer("Q", "A", "Dev", "Junior", "Tech")
        
        assert result is None

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.extract_technical_concepts')
    @patch('app.interview.answer_analyzer.get_wikipedia_context')
    @patch('app.interview.answer_analyzer.load_prompt')
    @patch('app.interview.answer_analyzer.call_llm')
    def test_analyze_answer_invalid_json_response(self, mock_call_llm, mock_load_prompt,
                                                mock_get_wiki_context, mock_extract_concepts):
        """Test handling of invalid JSON response from LLM"""
        mock_extract_concepts.return_value = ["Python"]
        mock_get_wiki_context.return_value = "Wiki context"
        mock_load_prompt.return_value = "template"
        mock_call_llm.return_value = "Not a JSON response"
        
        result = analyze_answer("Q", "A", "Dev", "Junior", "Tech")
        
        assert result is None

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.extract_technical_concepts')
    @patch('app.interview.answer_analyzer.get_wikipedia_context')
    @patch('app.interview.answer_analyzer.load_prompt')
    @patch('app.interview.answer_analyzer.call_llm')
    def test_analyze_answer_partial_json_response(self, mock_call_llm, mock_load_prompt,
                                                 mock_get_wiki_context, mock_extract_concepts):
        """Test handling of response with JSON embedded in text"""
        mock_extract_concepts.return_value = ["Python"]
        mock_get_wiki_context.return_value = "Wiki context"
        mock_load_prompt.return_value = "template"
        
        # Response with JSON embedded in text
        json_response = '{"score": 75, "feedback": "Good answer"}'
        mock_call_llm.return_value = f"Here is the analysis: {json_response} End of analysis."
        
        result = analyze_answer("Q", "A", "Dev", "Junior", "Tech")
        
        expected = {"score": 75, "feedback": "Good answer"}
        assert result == expected

    @pytest.mark.unit
    @patch('app.interview.answer_analyzer.extract_technical_concepts')
    @patch('app.interview.answer_analyzer.get_wikipedia_context')
    @patch('app.interview.answer_analyzer.load_prompt')
    @patch('app.interview.answer_analyzer.call_llm')
    def test_analyze_answer_no_json_in_response(self, mock_call_llm, mock_load_prompt,
                                              mock_get_wiki_context, mock_extract_concepts):
        """Test handling of response with no JSON content"""
        mock_extract_concepts.return_value = ["Python"]
        mock_get_wiki_context.return_value = "Wiki context"
        mock_load_prompt.return_value = "template"
        mock_call_llm.return_value = "This is just text with no JSON content"
        
        result = analyze_answer("Q", "A", "Dev", "Junior", "Tech")
        
        assert result is None

    @pytest.mark.integration
    @patch('app.interview.answer_analyzer.WikipediaService')
    def test_analyze_answer_integration_flow(self, mock_wiki_service_class):
        """Integration test for the complete analysis flow"""
        # Mock Wikipedia service
        mock_service = Mock()
        mock_wiki_service_class.return_value = mock_service
        mock_service.get_concept_summary.return_value = {
            "title": "Python",
            "extract": "Python is a programming language",
            "url": "https://wiki.com"
        }
        
        # Mock LLM calls
        with patch('app.interview.answer_analyzer.call_llm') as mock_call_llm:
            with patch('app.interview.answer_analyzer.load_prompt') as mock_load_prompt:
                # Mock concept extraction
                mock_load_prompt.side_effect = [
                    "Extract concepts from {answer}",
                    "Analyze: {question} {text}"
                ]
                mock_call_llm.side_effect = [
                    '["Python", "Django"]',  # Concept extraction
                    '{"score": 90, "feedback": "Excellent"}'  # Analysis
                ]
                
                result = analyze_answer(
                    "What is Python?",
                    "Python is a great programming language for web development",
                    "Backend Developer",
                    "Senior",
                    "Technical"
                )
                
                assert result["score"] == 90
                assert result["feedback"] == "Excellent"
                # Verify Wikipedia service was used
                mock_service.get_concept_summary.assert_called()
