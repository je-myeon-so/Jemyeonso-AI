import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app

client = TestClient(app)


class TestImproveEndpoints:
    """면접 개선점 분석 API 엔드포인트 테스트"""

    @pytest.mark.api
    @patch('app.router.interview.analyze_improvement')
    def test_improve_interview_success(self, mock_analyze):
        """면접 개선점 분석 성공 테스트"""
        mock_analyze.return_value = {
            "interviewId": 123,
            "overallComment": "전체적으로 좋은 답변을 하셨습니다. 기술적 지식이 탄탄하고 논리적으로 설명하는 능력이 뛰어납니다."
        }
        
        request_data = {
            "interviewId": 123,
            "jobType": "백엔드 개발자",
            "qaList": [
                {
                    "question": "자기소개를 해주세요.",
                    "answer": "안녕하세요. 백엔드 개발자로 3년간 경험을 쌓아온 김개발입니다."
                },
                {
                    "question": "데이터베이스 정규화에 대해 설명해주세요.",
                    "answer": "데이터베이스 정규화는 데이터의 중복을 제거하고 일관성을 유지하기 위한 과정입니다."
                }
            ]
        }
        
        response = client.post("/api/ai/improve", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "면접 종합 분석을 완료했습니다" in data["message"]
        assert "data" in data
        assert data["data"]["interviewId"] == 123
        assert "overallComment" in data["data"]
        assert "기술적 지식이 탄탄하고" in data["data"]["overallComment"]

    @pytest.mark.api
    @patch('app.router.interview.analyze_improvement')
    def test_improve_interview_analysis_error(self, mock_analyze):
        """면접 개선점 분석 실패 테스트"""
        mock_analyze.side_effect = Exception("분석 오류")
        
        request_data = {
            "interviewId": 456,
            "jobType": "프론트엔드 개발자",
            "qaList": [
                {
                    "question": "React의 특징은?",
                    "answer": "컴포넌트 기반 라이브러리입니다."
                }
            ]
        }
        
        response = client.post("/api/ai/improve", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 500
        assert "오류가 발생했습니다" in data["message"]
        assert data["data"]["interviewId"] == 456
        assert "오류가 발생했습니다" in data["data"]["overallComment"]

    @pytest.mark.api
    def test_improve_interview_missing_required_fields(self):
        """필수 필드 누락 테스트"""
        request_data = {
            "interviewId": 789,
            "jobType": "백엔드 개발자"
            # qaList 누락
        }
        
        response = client.post("/api/ai/improve", json=request_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.api
    @patch('app.router.interview.analyze_improvement')
    def test_improve_interview_empty_qa_list(self, mock_analyze):
        """빈 Q&A 리스트 테스트"""
        mock_analyze.return_value = {
            "interviewId": 789,
            "overallComment": "제공된 질문과 답변이 없어 분석할 수 없습니다."
        }
        
        request_data = {
            "interviewId": 789,
            "jobType": "풀스택 개발자",
            "qaList": []
        }
        
        response = client.post("/api/ai/improve", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["interviewId"] == 789
        assert "제공된 질문과 답변이 없어" in data["data"]["overallComment"]

    @pytest.mark.api
    @patch('app.router.interview.analyze_improvement')
    def test_improve_interview_multiple_qa_items(self, mock_analyze):
        """여러 Q&A 아이템 테스트"""
        mock_analyze.return_value = {
            "interviewId": 999,
            "overallComment": "다양한 질문에 대해 일관성 있게 답변하셨습니다. 특히 기술적 경험을 구체적으로 설명한 점이 인상적입니다."
        }
        
        request_data = {
            "interviewId": 999,
            "jobType": "백엔드 개발자",
            "qaList": [
                {
                    "question": "자기소개를 해주세요",
                    "answer": "안녕하세요. 백엔드 개발자입니다."
                },
                {
                    "question": "프로젝트 경험은?",
                    "answer": "3년간 다양한 프로젝트를 진행했습니다."
                },
                {
                    "question": "기술 스택은?",
                    "answer": "Python, Django, PostgreSQL을 주로 사용합니다."
                }
            ]
        }
        
        response = client.post("/api/ai/improve", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["interviewId"] == 999
        assert "일관성 있게 답변" in data["data"]["overallComment"]
        assert "기술적 경험을 구체적으로 설명" in data["data"]["overallComment"]

    @pytest.mark.api
    def test_improve_interview_invalid_interview_id(self):
        """잘못된 인터뷰 ID 타입 테스트"""
        request_data = {
            "interviewId": "invalid_id",  # 문자열이 아닌 정수여야 함
            "jobType": "백엔드 개발자",
            "qaList": [
                {
                    "question": "테스트 질문",
                    "answer": "테스트 답변"
                }
            ]
        }
        
        response = client.post("/api/ai/improve", json=request_data)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.api
    @patch('app.router.interview.analyze_improvement')
    def test_improve_interview_large_qa_list(self, mock_analyze):
        """큰 Q&A 리스트 테스트"""
        mock_analyze.return_value = {
            "interviewId": 1000,
            "overallComment": "포괄적인 면접이었습니다. 다양한 영역에 대한 질문에 잘 답변하셨습니다."
        }
        
        # 10개의 Q&A 아이템 생성
        qa_list = []
        for i in range(10):
            qa_list.append({
                "question": f"질문 {i+1}",
                "answer": f"답변 {i+1}"
            })
        
        request_data = {
            "interviewId": 1000,
            "jobType": "풀스택 개발자",
            "qaList": qa_list
        }
        
        response = client.post("/api/ai/improve", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["interviewId"] == 1000
        assert "포괄적인 면접이었습니다" in data["data"]["overallComment"]

    @pytest.mark.api
    def test_improve_interview_invalid_json(self):
        """잘못된 JSON 요청 테스트"""
        response = client.post(
            "/api/ai/improve",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        
        assert response.status_code == 422

    @pytest.mark.api
    @patch('app.router.interview.analyze_improvement')
    def test_improve_interview_special_characters_in_qa(self, mock_analyze):
        """Q&A에 특수문자가 포함된 경우 테스트"""
        mock_analyze.return_value = {
            "interviewId": 2000,
            "overallComment": "특수문자가 포함된 답변도 잘 처리되었습니다."
        }
        
        request_data = {
            "interviewId": 2000,
            "jobType": "백엔드 개발자",
            "qaList": [
                {
                    "question": "프로그래밍 언어에 대해 어떻게 생각하시나요?",
                    "answer": "Python은 정말 좋습니다! 🐍 특히 Django 프레임워크는 웹 개발에 최적화되어 있어요. & 그리고 PostgreSQL과의 연동도 매우 편리합니다."
                }
            ]
        }
        
        response = client.post("/api/ai/improve", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["interviewId"] == 2000
        assert "특수문자가 포함된 답변도" in data["data"]["overallComment"]
