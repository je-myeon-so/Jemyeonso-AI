"""
Tests for Pydantic schemas and data validation
"""
import pytest
from pydantic import ValidationError


class TestInterviewSchemas:
    """Test cases for interview-related schemas"""

    @pytest.mark.unit
    def test_question_generation_request_valid(self):
        """Test valid question generation request schema"""
        try:
            from app.schemas.interview import GenerateQuestionRequest
            
            valid_data = {
                "questionLevel": "중급",
                "jobType": "Backend Developer", 
                "questionCategory": "기술",
                "documentId": 123
            }
            
            request = GenerateQuestionRequest(**valid_data)
            
            assert request.questionLevel == "중급"
            assert request.jobType == "Backend Developer"
            assert request.questionCategory == "기술"
            assert request.documentId == 123
            
        except ImportError:
            pytest.skip("Interview schemas not available")

    @pytest.mark.unit
    def test_question_generation_request_invalid(self):
        """Test invalid question generation request schema"""
        try:
            from app.schemas.interview import GenerateQuestionRequest
            
            # Test missing required fields
            with pytest.raises(ValidationError):
                GenerateQuestionRequest(jobType="test")
            
            # Test invalid documentId (should be int)
            with pytest.raises(ValidationError):
                GenerateQuestionRequest(
                    questionLevel="중급",
                    jobType="Developer",
                    questionCategory="기술",
                    documentId="invalid"
                )
                
        except ImportError:
            pytest.skip("Interview schemas not available")

    @pytest.mark.unit
    def test_answer_analysis_request_valid(self):
        """Test valid answer analysis request schema"""
        try:
            from app.schemas.interview import AnalyzeAnswerRequest
            
            valid_data = {
                "question": "What is Python?",
                "answer": "Python is a programming language...",
                "jobType": "Developer",
                "questionLevel": "중급",
                "questionCategory": "기술"
            }
            
            request = AnalyzeAnswerRequest(**valid_data)
            
            assert request.question == "What is Python?"
            assert request.answer == "Python is a programming language..."
            assert request.jobType == "Developer"
            assert request.questionLevel == "중급"
            assert request.questionCategory == "기술"
            
        except ImportError:
            pytest.skip("Interview schemas not available")

    @pytest.mark.unit
    def test_korean_text_validation(self):
        """Test that schemas properly handle Korean text"""
        try:
            from app.schemas.interview import GenerateQuestionRequest
            
            korean_data = {
                "questionLevel": "고급",
                "jobType": "백엔드 개발자",
                "questionCategory": "기술",
                "documentId": 456
            }
            
            request = GenerateQuestionRequest(**korean_data)
            
            assert request.jobType == "백엔드 개발자"
            assert request.questionLevel == "고급"
            assert request.questionCategory == "기술"
            
        except ImportError:
            pytest.skip("Interview schemas not available")

    @pytest.mark.unit
    def test_special_characters_validation(self):
        """Test schemas handle special characters and emojis"""
        try:
            from app.schemas.interview import AnalyzeAnswerRequest
            
            special_data = {
                "question": "What's your favorite language? 🤔",
                "answer": "I ❤️ Python! It's 100% awesome for AI/ML & web dev.",
                "jobType": "AI/ML Engineer",
                "questionLevel": "중급",
                "questionCategory": "기술"
            }
            
            request = AnalyzeAnswerRequest(**special_data)
            
            assert "🤔" in request.question
            assert "❤️" in request.answer
            assert "AI/ML" in request.jobType
            
        except ImportError:
            pytest.skip("Interview schemas not available")


class TestResumeSchemas:
    """Test cases for resume-related schemas"""

    @pytest.mark.unit
    def test_resume_process_request_schema(self):
        """Test resume process request schema"""
        try:
            from app.schemas.resume import ResumeProcessRequest
            
            request_data = {
                "fileUrl": "https://example.com/resume.pdf",
                "userId": 123,
                "documentId": 456,
                "fileType": "pdf"
            }
            
            request = ResumeProcessRequest(**request_data)
            
            assert str(request.fileUrl) == "https://example.com/resume.pdf"
            assert request.userId == 123
            assert request.documentId == 456
            assert request.fileType == "pdf"
            
        except ImportError:
            pytest.skip("Resume schemas not available")

    @pytest.mark.unit
    def test_resume_process_request_invalid(self):
        """Test invalid resume process request"""
        try:
            from app.schemas.resume import ResumeProcessRequest
            
            # Test invalid URL
            with pytest.raises(ValidationError):
                ResumeProcessRequest(
                    fileUrl="not-a-url",
                    userId=123,
                    documentId=456,
                    fileType="pdf"
                )
            
            # Test missing required fields
            with pytest.raises(ValidationError):
                ResumeProcessRequest(fileUrl="https://example.com/file.pdf")
                
        except ImportError:
            pytest.skip("Resume schemas not available")


class TestSchemaIntegration:
    """Integration tests for schemas with business logic"""

    @pytest.mark.integration
    def test_schema_with_actual_data_flow(self):
        """Test schemas work with actual data flow"""
        try:
            from app.schemas.interview import GenerateQuestionRequest, AnalyzeAnswerRequest
            
            # Simulate realistic data flow
            question_request = GenerateQuestionRequest(
                questionLevel="고급",
                jobType="백엔드 개발자",
                questionCategory="기술",
                documentId=789
            )
            
            # Data should be properly structured for business logic
            assert question_request.jobType == "백엔드 개발자"
            assert question_request.questionLevel == "고급"
            
            # Simulate answer analysis flow
            analysis_request = AnalyzeAnswerRequest(
                question="Django와 FastAPI의 차이점을 설명해주세요.",
                answer="Django는 풀스택 프레임워크이고 FastAPI는 API 전용 프레임워크입니다...",
                jobType="백엔드 개발자",
                questionLevel="고급",
                questionCategory="기술"
            )
            
            assert len(analysis_request.answer) > 0
            assert analysis_request.questionCategory == "기술"
            
        except ImportError:
            pytest.skip("Interview schemas not available")
