"""
Integration Tests for Enhanced Interview Analysis System
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json
import threading
import time


@pytest.mark.integration
class TestEnhancedInterviewAnalysis:
    """Integration tests for the complete enhanced interview analysis system"""

    def test_enhanced_analyze_answer_api_success(self, client):
        """Test the enhanced analyze answer API endpoint"""
        
        mock_llm_response = '''
        {
          "score": 88,
          "analysis": [
            {
              "errorText": "구체적인 예시 부족",
              "errorType": "깊이_부족",
              "feedback": "답변에 구체적인 프로젝트 경험이나 예시가 부족합니다",
              "suggestion": "실제로 경험한 프로젝트나 구체적인 사례를 추가해보세요"
            }
          ]
        }
        '''
        
        with patch('app.core.llm_utils.call_llm') as mock_llm:
            mock_llm.side_effect = [
                '["Python", "Django", "REST API"]',  # For concept extraction
                mock_llm_response  # For analysis
            ]
            
            response = client.post("/api/ai/answers/analyze", json={
                "questionCategory": "기술",
                "questionLevel": "중급",
                "jobType": "백엔드 개발자",
                "question": "Python과 Django를 사용한 REST API 개발 경험에 대해 설명해주세요",
                "answer": "Python과 Django를 사용하여 REST API를 개발한 경험이 있습니다."
            })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["code"] == 200
        assert "data" in data
        assert "score" in data["data"]
        assert "analysis" in data["data"]
        assert 0 <= data["data"]["score"] <= 100
        assert data["data"]["score"] == 88
        
        analysis_items = data["data"]["analysis"]
        assert len(analysis_items) == 1
        assert "errorText" in analysis_items[0]
        assert "errorType" in analysis_items[0]
        assert "feedback" in analysis_items[0]
        assert "suggestion" in analysis_items[0]
        assert analysis_items[0]["errorType"] == "깊이_부족"

    def test_enhanced_analyze_answer_perfect_score(self, client):
        """Test analysis with perfect score"""
        
        mock_llm_response = '{"score": 100, "analysis": []}'
        
        with patch('app.core.llm_utils.call_llm') as mock_llm:
            mock_llm.side_effect = ['["React"]', mock_llm_response]
            
            response = client.post("/api/ai/answers/analyze", json={
                "questionCategory": "기술",
                "questionLevel": "시니어",
                "jobType": "프론트엔드 개발자",
                "question": "React의 장점은?",
                "answer": "React는 가상 DOM, 컴포넌트 기반 아키텍처 등의 장점이 있습니다."
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["score"] == 100
        assert data["data"]["analysis"] == []

    def test_enhanced_analyze_answer_with_fallback(self, client):
        """Test analysis with fallback when LLM fails"""
        
        with patch('app.core.llm_utils.call_llm') as mock_llm:
            mock_llm.side_effect = [
                '["Python"]',
                ConnectionError("Network error")
            ]
            
            response = client.post("/api/ai/answers/analyze", json={
                "questionCategory": "기술",
                "questionLevel": "초급",
                "jobType": "개발자",
                "question": "프로그래밍이란?",
                "answer": "프로그래밍은 컴퓨터에게 명령을 내리는 것입니다"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert "score" in data["data"]
        assert 0 <= data["data"]["score"] <= 100
        assert isinstance(data["data"]["analysis"], list)
