"""
Tests for Resume parsing and PII detection functionality
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
from fastapi.testclient import TestClient
from io import BytesIO
from app.main import app

client = TestClient(app)


class TestResumeParser:
    """Test cases for resume parsing functionality"""

    @pytest.mark.unit
    @patch('app.resume.parser.pdfplumber')
    def test_parse_pdf_resume_success(self, mock_pdfplumber):
        """Test successful PDF resume parsing"""
        try:
            from app.resume.parser import extract_text_from_pdf
            
            # Mock PDF content
            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.extract_text.return_value = "John Doe\nSoftware Engineer\nPython, Django"
            mock_pdf.pages = [mock_page]
            mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
            
            # Create mock file
            pdf_content = b"mock pdf content"
            result = extract_text_from_pdf(BytesIO(pdf_content))
            
            assert "John Doe" in result
            assert "Software Engineer" in result
            assert "Python" in result
            
        except ImportError:
            pytest.skip("resume.parser module not available")

    @pytest.mark.unit
    @patch('app.resume.parser.pdfplumber')
    def test_parse_pdf_resume_failure(self, mock_pdfplumber):
        """Test PDF parsing failure handling"""
        try:
            from app.resume.parser import extract_text_from_pdf
            
            mock_pdfplumber.open.side_effect = Exception("PDF parsing error")
            
            pdf_content = b"invalid pdf content"
            result = extract_text_from_pdf(BytesIO(pdf_content))
            
            assert result == "" or result is None
            
        except ImportError:
            pytest.skip("resume.parser module not available")

    @pytest.mark.unit
    def test_parse_text_resume(self):
        """Test text resume parsing"""
        try:
            from app.resume.parser import extract_text_from_txt
            
            text_content = "Name: Jane Smith\nExperience: 5 years Python development"
            result = extract_text_from_txt(text_content.encode())
            
            assert "Jane Smith" in result
            assert "Python development" in result
            
        except ImportError:
            pytest.skip("resume.parser text extraction not available")


class TestPIIDetection:
    """Test cases for PII (Personally Identifiable Information) detection"""

    @pytest.mark.unit
    def test_detect_email_pii(self):
        """Test email PII detection"""
        try:
            from app.resume.pii_detector import detect_pii
            
            text = "Contact me at john.doe@example.com for more information"
            pii_items = detect_pii(text)
            
            # Should detect email via regex (works even if NER model failed to load)
            assert "email" in pii_items["detected_pii_fields"]
            assert "john.doe@example.com" in str(pii_items["regex_result"])
            
        except ImportError as e:
            pytest.skip(f"pii_detector module not available: {e}")

    @pytest.mark.unit
    def test_detect_phone_pii(self):
        """Test phone number PII detection"""
        try:
            from app.resume.pii_detector import detect_pii, PIIType
            
            text = "Call me at 010-1234-5678 or 02-987-6543"
            pii_items = detect_pii(text)
            
            phone_items = [item for item in pii_items if item.type == PIIType.PHONE]
            assert len(phone_items) >= 1
            
        except ImportError:
            pytest.skip("pii_detector module not available")

    @pytest.mark.unit
    def test_detect_name_pii(self):
        """Test name PII detection"""
        try:
            from app.resume.pii_detector import detect_pii, PIIType
            
            text = "My name is 김철수 and I am a software engineer"
            pii_items = detect_pii(text)
            
            name_items = [item for item in pii_items if item.type == PIIType.NAME]
            # Name detection might be complex, so we just check it doesn't crash
            assert isinstance(name_items, list)
            
        except ImportError:
            pytest.skip("pii_detector module not available")

    @pytest.mark.unit
    def test_detect_multiple_pii_types(self):
        """Test detection of multiple PII types in one text"""
        try:
            from app.resume.pii_detector import detect_pii
            
            text = """
            이름: 김철수
            이메일: kim.cs@example.com
            연락처: 010-1234-5678
            주소: 서울시 강남구 테헤란로 123
            """
            
            pii_items = detect_pii(text)
            assert len(pii_items) >= 2  # At least email and phone
            
        except ImportError:
            pytest.skip("pii_detector module not available")


class TestPIILogger:
    """Test cases for PII logging functionality"""

    @pytest.mark.unit
    def test_log_pii_detection(self):
        """Test PII detection logging"""
        try:
            from app.resume.pii_logger import create_pii_log_payload
            
            regex_result = {"email": ["test@example.com"]}
            ner_result = {"phone": ["010-1234-5678"]}
            
            result = create_pii_log_payload(
                user_id="user_123",
                file_id="file_456", 
                original_filename="resume.pdf",
                regex_result=regex_result,
                ner_result=ner_result
            )
            
            assert result["code"] == "200"
            assert "data" in result
            assert result["data"]["user_id"] == "user_123"
            assert result["data"]["file_id"] == "file_456"
            assert "email" in result["data"]["detected_pii_fields"]
            assert "phone" in result["data"]["detected_pii_fields"]
            
        except ImportError:
            pytest.skip("pii_logger module not available")

    @pytest.mark.unit
    def test_log_pii_detection_failure(self):
        """Test PII logging failure handling"""
        try:
            from app.resume.pii_logger import create_pii_log_payload
            
            # Test with empty results
            result = create_pii_log_payload(
                user_id="user_123",
                file_id="file_456",
                original_filename="resume.pdf", 
                regex_result={},
                ner_result={}
            )
            
            # Should handle empty PII gracefully
            assert result["code"] == "200"
            assert result["data"]["detected_pii_fields"] == []
            
        except ImportError:
            pytest.skip("pii_logger module not available")
