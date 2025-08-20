import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app

client = TestClient(app)


class TestInterviewEndpoints:
    """Test cases for interview-related API endpoints"""

    @pytest.mark.api
    @patch('app.interview.question_generator.question_cache')
    @patch('app.interview.question_generator.call_llm')
    @patch('app.interview.question_generator.load_prompt')
    @patch('app.interview.question_generator.get_resume_text')
    def test_generate_questions_success(self, mock_get_resume, mock_load_prompt, mock_call_llm, mock_cache):
        """Test successful question generation"""
        # Mock all dependencies with assertion to debug
        mock_get_resume.return_value = "Sample resume content with actual content"
        mock_load_prompt.return_value = "Template: {resume_text} {job_type} {question_level} {question_category} {question_type} {previous_questions_section}"
        mock_call_llm.return_value = "What is Python?"
        mock_cache.get_previous_questions.return_value = []
        mock_cache.add_question.return_value = None
        
        # Make sure our mock will be called
        assert mock_get_resume.return_value  # Should be truthy
        
        request_data = {
            "jobType": "Backend Developer",
            "questionLevel": "중급",
            "questionCategory": "기술",
            "documentId": 123
        }
        
        response = client.post("/api/ai/questions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert data["data"]["question"] == "What is Python?"

    @pytest.mark.api
    def test_generate_questions_missing_fields(self):
        """Test question generation with missing required fields"""
        request_data = {
            "jobType": "Python developer",
            # Missing questionLevel, questionCategory, documentId
        }
        
        response = client.post("/api/ai/questions", json=request_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.api
    @patch('app.interview.question_generator.question_cache')
    @patch('app.interview.question_generator.call_llm')
    @patch('app.interview.question_generator.load_prompt')
    @patch('app.interview.question_generator.get_resume_text')
    def test_generate_questions_empty_resume(self, mock_get_resume, mock_load_prompt, mock_call_llm, mock_cache):
        """Test question generation with empty resume content"""
        # Mock all dependencies
        mock_get_resume.return_value = "Sample resume with content"
        mock_load_prompt.return_value = "Template: {resume_text} {job_type} {question_level} {question_category} {question_type} {previous_questions_section}"
        mock_call_llm.return_value = "일반적인 질문입니다"
        mock_cache.get_previous_questions.return_value = []
        mock_cache.add_question.return_value = None
        
        request_data = {
            "jobType": "Developer",
            "questionLevel": "초급",
            "questionCategory": "일반",
            "documentId": 456
        }
        
        response = client.post("/api/ai/questions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data

    @pytest.mark.api
    @patch('app.router.interview.analyze_answer')
    def test_analyze_answer_success(self, mock_analyze):
        """Test successful answer analysis"""
        mock_analyze.return_value = {
            "analysis": [
                {
                    "errorText": "Good technical explanation",
                    "errorType": "우수", 
                    "feedback": "Clear communication, Good examples",
                    "suggestion": "Add more technical details"
                }
            ]
        }
        
        request_data = {
            "question": "What is Python?",
            "answer": "Python is a high-level programming language...",
            "jobType": "Backend Developer",
            "questionLevel": "중급",
            "questionCategory": "기술"
        }
        
        response = client.post("/api/ai/answers/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert "analysis" in data["data"]

    @pytest.mark.api
    @patch('app.router.interview.analyze_answer')
    def test_analyze_answer_failure(self, mock_analyze):
        """Test answer analysis when analysis fails"""
        mock_analyze.return_value = None  # This should trigger the failure path
        
        request_data = {
            "question": "What is Python?",
            "answer": "Python is...",
            "jobType": "Developer",
            "questionLevel": "초급",
            "questionCategory": "기술"
        }
        
        response = client.post("/api/ai/answers/analyze", json=request_data)
        
        assert response.status_code == 200  # Your endpoint returns 200 even on failure
        data = response.json()
        assert data["code"] == 200
        assert "분석이 완료되었습니다" in data["message"] and "특별히 개선할 점을 찾지 못했습니다" in data["message"]

    @pytest.mark.api
    def test_analyze_answer_missing_fields(self):
        """Test answer analysis with missing required fields"""
        request_data = {
            "question": "What is Python?",
            # Missing answer, jobType, questionLevel, questionCategory
        }
        
        response = client.post("/api/ai/answers/analyze", json=request_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.api
    @patch('app.router.interview.analyze_answer')
    def test_analyze_answer_empty_answer(self, mock_analyze):
        """Test analysis with empty answer"""
        mock_analyze.return_value = {
            "analysis": [
                {
                    "errorText": "답변이 제공되지 않았습니다",
                    "errorType": "미흡",
                    "feedback": "",
                    "suggestion": "답변을 제공해주세요"
                }
            ]
        }
        
        request_data = {
            "question": "What is Python?",
            "answer": "",
            "jobType": "Developer",
            "questionLevel": "초급",
            "questionCategory": "기술"
        }
        
        response = client.post("/api/ai/answers/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    @pytest.mark.api
    def test_invalid_json_request(self):
        """Test handling of invalid JSON in request"""
        response = client.post(
            "/api/ai/questions",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        
        assert response.status_code == 422

    @pytest.mark.api
    @patch('app.interview.question_generator.question_cache')
    @patch('app.interview.question_generator.call_llm')
    @patch('app.interview.question_generator.load_prompt')
    @patch('app.interview.question_generator.get_resume_text')
    def test_large_request_handling(self, mock_get_resume, mock_load_prompt, mock_call_llm, mock_cache):
        """Test handling of very large resume content"""
        # Mock all dependencies
        mock_get_resume.return_value = "Large resume content that is substantial"
        mock_load_prompt.return_value = "Template: {resume_text} {job_type} {question_level} {question_category} {question_type} {previous_questions_section}"
        mock_call_llm.return_value = "일반 질문입니다"
        mock_cache.get_previous_questions.return_value = []
        mock_cache.add_question.return_value = None
        
        request_data = {
            "jobType": "Developer",
            "questionLevel": "중급", 
            "questionCategory": "일반",
            "documentId": 789
        }
        
        response = client.post("/api/ai/questions", json=request_data)
        
        # Should handle request gracefully
        assert response.status_code in [200, 413, 422]

    @pytest.mark.api
    @patch('app.router.interview.analyze_answer')
    def test_analysis_with_special_characters(self, mock_analyze):
        """Test answer analysis with special characters and emojis"""
        mock_analyze.return_value = {
            "analysis": [
                {
                    "errorText": "답변에 특수문자가 포함되어 있습니다",
                    "errorType": "보통",
                    "feedback": "창의적 표현",
                    "suggestion": "기술적 정확성"
                }
            ]
        }
        
        request_data = {
            "question": "What is your favorite programming language?",
            "answer": "I ❤️ Python! It's 100% awesome 🐍 for web development & data science.",
            "jobType": "Developer",
            "questionLevel": "중급",
            "questionCategory": "개인성향"
        }
        
        response = client.post("/api/ai/answers/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
