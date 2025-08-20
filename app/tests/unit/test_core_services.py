"""
Tests for Core Services and Utilities
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
import json


class TestLLMUtils:
    """Test cases for LLM utility functions"""

    @pytest.mark.unit
    @patch('app.core.llm_utils.client')
    def test_call_llm_success(self, mock_client):
        """Test successful LLM call"""
        from app.core.llm_utils import call_llm
        
        # Mock completion response
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_completion
        
        result = call_llm(
            prompt="Test prompt",
            temperature=0.5,
            max_tokens=100,
            system_role="Test role"
        )
        
        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.unit
    @patch('app.core.llm_utils.client')
    def test_call_llm_exception(self, mock_client):
        """Test LLM call with exception"""
        from app.core.llm_utils import call_llm
        
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Your function returns error message instead of raising exception
        result = call_llm("Test prompt")
        assert result == "질문 생성 중 오류가 발생했습니다."


class TestQuestionCache:
    """Test cases for Question Cache functionality"""

    @pytest.mark.unit
    def test_cache_questions(self):
        """Test caching questions"""
        from app.core.question_cache import question_cache
        
        # Test adding a question
        question_cache.add_question(
            document_id="doc123",
            job_type="Developer", 
            question_category="기술",
            question_level="중급",
            question="Test question"
        )
        
        # Test retrieving questions
        questions = question_cache.get_previous_questions(
            document_id="doc123",
            job_type="Developer",
            question_category="기술", 
            question_level="중급"
        )
        
        assert "Test question" in questions

    @pytest.mark.unit
    def test_get_cached_questions(self):
        """Test retrieving cached questions"""
        from app.core.question_cache import question_cache
        
        # Clear any existing cache first
        question_cache.clear_cache_by_document("test_doc")
        
        # Add a question
        question_cache.add_question(
            document_id="test_doc",
            job_type="Backend Developer",
            question_category="기술",
            question_level="고급", 
            question="Cached test question"
        )
        
        # Retrieve questions
        result = question_cache.get_previous_questions(
            document_id="test_doc",
            job_type="Backend Developer", 
            question_category="기술",
            question_level="고급"
        )
        
        assert len(result) == 1
        assert "Cached test question" in result


class TestRegexUtils:
    """Test cases for Regex utility functions"""

    @pytest.mark.unit
    def test_email_detection(self):
        """Test email pattern detection"""
        try:
            from app.core.regex_utils import PII_PATTERNS
            import re
            
            email_pattern = PII_PATTERNS["email"]
            test_cases = [
                ("test@example.com", True),
                ("user.name@domain.co.kr", True),
                ("invalid.email", False),
                ("@example.com", False),
                ("test@", False)
            ]
            
            for email, should_match in test_cases:
                match = re.search(email_pattern, email)
                assert bool(match) == should_match
                
        except ImportError:
            pytest.skip("regex_utils module not available")

    @pytest.mark.unit
    def test_phone_detection(self):
        """Test phone number pattern detection"""
        try:
            from app.core.regex_utils import PII_PATTERNS
            import re
            
            phone_pattern = PII_PATTERNS["phone"]
            test_cases = [
                ("010-1234-5678", True),
                ("01012345678", True),
                ("02-123-4567", False),  # This pattern doesn't match 02 numbers
                ("invalid-phone", False),
                ("123", False)
            ]
            
            for phone, should_match in test_cases:
                match = re.search(phone_pattern, phone)
                assert bool(match) == should_match
                
        except ImportError:
            pytest.skip("regex_utils module not available")


class TestS3Utils:
    """Test cases for S3 utility functions"""

    @pytest.mark.unit
    @patch('app.core.s3_utils.s3')
    def test_s3_upload_success(self, mock_s3_client):
        """Test successful S3 file upload"""
        try:
            from app.core.s3_utils import upload_file_to_s3
            
            mock_s3_client.put_object.return_value = None
            
            # Test file bytes
            test_content = b"test content"
            
            result = upload_file_to_s3(test_content, "test-key", "text/plain")
            
            assert result is True
            mock_s3_client.put_object.assert_called_once()
            
        except ImportError:
            pytest.skip("s3_utils module not available")

    @pytest.mark.unit
    @patch('app.core.s3_utils.s3')
    def test_s3_upload_failure(self, mock_s3_client):
        """Test S3 upload failure handling"""
        try:
            from app.core.s3_utils import upload_file_to_s3
            
            mock_s3_client.put_object.side_effect = Exception("S3 Error")
            
            test_content = b"test content"
            
            # Should handle exception gracefully
            result = upload_file_to_s3(test_content, "test-key")
            assert result is False
            
        except ImportError:
            pytest.skip("s3_utils module not available")


class TestMySQLUtils:
    """Test cases for MySQL utility functions"""

    @pytest.mark.unit
    @patch('app.core.mysql_utils.get_connection')
    def test_database_connection(self, mock_get_connection):
        """Test MySQL database connection"""
        try:
            from app.core.mysql_utils import get_resume_text
            
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = ("Test content",)
            mock_cursor.__enter__ = Mock(return_value=mock_cursor)
            mock_cursor.__exit__ = Mock(return_value=None)
            mock_connection.cursor.return_value = mock_cursor
            mock_get_connection.return_value = mock_connection
            
            result = get_resume_text("test-doc-id")
            
            assert result == "Test content"
            mock_get_connection.assert_called_once()
            
        except ImportError:
            pytest.skip("mysql_utils module not available")

    @pytest.mark.unit
    @patch('app.core.mysql_utils.get_connection')
    def test_database_connection_failure(self, mock_get_connection):
        """Test MySQL connection failure handling"""
        try:
            from app.core.mysql_utils import get_resume_text
            
            mock_get_connection.return_value = None
            
            result = get_resume_text("test-doc-id")
            assert result is None
            
        except ImportError:
            pytest.skip("mysql_utils module not available")


class TestPromptLoader:
    """Test cases for Prompt Loader functionality"""

    @pytest.mark.unit
    @patch('app.interview.prompt_loader._prompt_cache')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_load_prompt_success(self, mock_read_text, mock_exists, mock_cache):
        """Test successful prompt loading"""
        from app.interview.prompt_loader import load_prompt
        
        mock_cache.get.return_value = None  # Not cached
        mock_exists.return_value = True
        mock_read_text.return_value = "Test prompt template with {variable}"
        
        result = load_prompt("test_prompt.txt")
        
        assert result == "Test prompt template with {variable}"
        mock_read_text.assert_called_once_with(encoding="utf-8")
        mock_cache.set.assert_called_once()

    @pytest.mark.unit
    @patch('pathlib.Path.exists')
    def test_load_prompt_file_not_found(self, mock_exists):
        """Test prompt loading when file doesn't exist"""
        from app.interview.prompt_loader import load_prompt
        
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            load_prompt("nonexistent_prompt.txt")

    @pytest.mark.unit
    def test_preload_prompts(self):
        """Test prompt preloading functionality"""
        try:
            from app.interview.prompt_loader import preload_prompts
            
            # Should not raise any exceptions
            preload_prompts()
            
        except ImportError:
            pytest.skip("preload_prompts function not available")


class TestIntegrationWithWikipedia:
    """Integration tests combining multiple services including Wikipedia"""

    @pytest.mark.integration
    @patch('app.interview.answer_analyzer.WikipediaService')
    @patch('app.interview.answer_analyzer.call_llm')
    def test_complete_analysis_flow_with_wikipedia(self, mock_call_llm, mock_wiki_service):
        """Test complete answer analysis flow including Wikipedia integration"""
        from app.interview.answer_analyzer import analyze_answer
        
        # Mock Wikipedia service
        mock_service = Mock()
        mock_wiki_service.return_value = mock_service
        mock_service.get_concept_summary.return_value = {
            "title": "Python",
            "extract": "Python is a programming language",
            "url": "https://wiki.com"
        }
        
        # Mock LLM responses
        mock_call_llm.side_effect = [
            '["Python", "Django"]',  # Concept extraction
            json.dumps({  # Analysis - must have "analysis" key
                "analysis": [{
                    "errorText": "Python is a great language for web development",
                    "errorType": "전문성 우수", 
                    "feedback": "Good answer with Wikipedia context",
                    "suggestion": "Add more examples"
                }]
            })
        ]
        
        with patch('app.interview.answer_analyzer.load_prompt') as mock_load_prompt:
            mock_load_prompt.side_effect = [
                "Extract: {answer} for {job_type}",  # Concept extraction prompt
                "Analyze: {question} {text} {jobtype} {level} {category}"  # Analysis prompt
            ]
            
            result = analyze_answer(
                "What is Python?",
                "Python is a great language for web development",
                "Backend Developer", 
                "Junior",
                "Technical"
            )
            
            # The function should return a proper result with analysis
            assert result is not None
            assert result.get("analysis") is not None
            assert len(result["analysis"]) > 0
            
            # Verify Wikipedia service was called
            assert mock_wiki_service.called
            
            # Verify LLM was called for both concept extraction and analysis
            assert mock_call_llm.call_count == 2
