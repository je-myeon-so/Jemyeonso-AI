import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app.interview.improvement_analyzer import (
    format_qa_list,
    generate_overall_analysis_prompt,
    analyze_improvement
)
from app.schemas.interview import QAItem


class TestImprovementAnalyzer:
    """면접 개선점 분석기 유닛 테스트"""
    
    def test_format_qa_list_basic(self):
        """Q&A 리스트 기본 포맷팅 테스트"""
        qa_list = [
            QAItem(question="질문1", answer="답변1"),
            QAItem(question="질문2", answer="답변2")
        ]
        
        result = format_qa_list(qa_list)
        
        # 기본 구조 확인
        assert "질문 1:" in result
        assert "질문1" in result
        assert "답변 1:" in result
        assert "답변1" in result
        assert "질문 2:" in result
        assert "질문2" in result
        assert "답변 2:" in result
        assert "답변2" in result
        assert "-" * 50 in result
        
        # 구분선이 올바르게 포함되어 있는지 확인
        lines = result.split('\n')
        separator_count = sum(1 for line in lines if line.strip() == "-" * 50)
        assert separator_count == 2  # Q&A 2개에 대한 구분선
    
    def test_format_qa_list_empty(self):
        """빈 Q&A 리스트 테스트"""
        result = format_qa_list([])
        assert result == ""
    
    def test_format_qa_list_single_item(self):
        """단일 Q&A 아이템 테스트"""
        qa_list = [QAItem(question="단일 질문", answer="단일 답변")]
        
        result = format_qa_list(qa_list)
        
        assert "질문 1:" in result
        assert "단일 질문" in result
        assert "답변 1:" in result
        assert "단일 답변" in result
        assert "-" * 50 in result
    
    def test_generate_overall_analysis_prompt_success(self):
        """프롬프트 생성 성공 테스트"""
        qa_list = [QAItem(question="테스트 질문", answer="테스트 답변")]
        
        mock_template = "직무: {job_type}\nQ&A: {qa_content}\n분석해주세요."
        
        with patch('app.interview.improvement_analyzer.load_prompt') as mock_load:
            mock_load.return_value = mock_template
            
            prompt = generate_overall_analysis_prompt("백엔드 개발자", qa_list)
            
            assert "백엔드 개발자" in prompt
            assert "테스트 질문" in prompt
            assert "테스트 답변" in prompt
            assert "분석해주세요" in prompt
            mock_load.assert_called_once_with("improvement_analysis.txt")
    
    def test_generate_overall_analysis_prompt_file_not_found(self):
        """프롬프트 파일 없을 때 폴백 테스트"""
        qa_list = [QAItem(question="테스트 질문", answer="테스트 답변")]
        
        with patch('app.interview.improvement_analyzer.load_prompt') as mock_load:
            mock_load.side_effect = FileNotFoundError()
            
            prompt = generate_overall_analysis_prompt("백엔드 개발자", qa_list)
            
            # 폴백 프롬프트 확인
            assert "백엔드 개발자" in prompt
            assert "테스트 질문" in prompt
            assert "테스트 답변" in prompt
            assert "JSON 형식으로 응답해주세요" in prompt
            assert "overallComment" in prompt
    
    def test_generate_overall_analysis_prompt_general_error(self):
        """일반적인 프롬프트 로드 오류 테스트"""
        qa_list = [QAItem(question="테스트 질문", answer="테스트 답변")]
        
        with patch('app.interview.improvement_analyzer.load_prompt') as mock_load:
            mock_load.side_effect = Exception("일반 오류")
            
            prompt = generate_overall_analysis_prompt("백엔드 개발자", qa_list)
            
            # 최종 폴백 프롬프트 확인
            assert "백엔드 개발자" in prompt
            assert "테스트 질문" in prompt
            assert "테스트 답변" in prompt
            assert "분석 결과를 작성해주세요" in prompt
    
    def test_analyze_improvement_success(self):
        """면접 분석 성공 케이스 테스트"""
        qa_list = [QAItem(question="테스트 질문", answer="테스트 답변")]
        mock_llm_response = '{"overallComment": "전체적으로 좋은 답변을 하셨습니다. 기술적 지식이 탄탄하고 논리적으로 설명하는 능력이 뛰어납니다."}'
        
        with patch('app.interview.improvement_analyzer.generate_overall_analysis_prompt') as mock_prompt, \
             patch('app.interview.improvement_analyzer.call_llm', return_value=mock_llm_response):
            
            mock_prompt.return_value = "테스트 프롬프트"
            
            result = analyze_improvement(
                interview_id=123,
                job_type="백엔드 개발자",
                qa_list=qa_list
            )
            
            # 결과 구조 확인
            assert result["interviewId"] == 123
            assert result["overallComment"] == "전체적으로 좋은 답변을 하셨습니다. 기술적 지식이 탄탄하고 논리적으로 설명하는 능력이 뛰어납니다."
            
            # 함수 호출 확인
            mock_prompt.assert_called_once_with("백엔드 개발자", qa_list)
    
    def test_analyze_improvement_json_parse_error(self):
        """JSON 파싱 오류 테스트"""
        qa_list = [QAItem(question="테스트 질문", answer="테스트 답변")]
        mock_llm_response = 'Invalid JSON response without proper structure'
        
        with patch('app.interview.improvement_analyzer.generate_overall_analysis_prompt') as mock_prompt, \
             patch('app.interview.improvement_analyzer.call_llm', return_value=mock_llm_response):
            
            mock_prompt.return_value = "테스트 프롬프트"
            
            result = analyze_improvement(
                interview_id=123,
                job_type="백엔드 개발자",
                qa_list=qa_list
            )
            
            assert result["interviewId"] == 123
            assert "분석 결과를 받아올 수 없습니다" in result["overallComment"]
    
    def test_analyze_improvement_no_json_response(self):
        """JSON 응답이 없을 때 테스트"""
        qa_list = [QAItem(question="테스트 질문", answer="테스트 답변")]
        mock_llm_response = 'This is a plain text response without any JSON structure'
        
        with patch('app.interview.improvement_analyzer.generate_overall_analysis_prompt') as mock_prompt, \
             patch('app.interview.improvement_analyzer.call_llm', return_value=mock_llm_response):
            
            mock_prompt.return_value = "테스트 프롬프트"
            
            result = analyze_improvement(
                interview_id=123,
                job_type="백엔드 개발자",
                qa_list=qa_list
            )
            
            assert result["interviewId"] == 123
            assert "분석 결과를 받아올 수 없습니다" in result["overallComment"]
    
    def test_analyze_improvement_llm_error(self):
        """LLM 호출 오류 테스트"""
        qa_list = [QAItem(question="테스트 질문", answer="테스트 답변")]
        
        with patch('app.interview.improvement_analyzer.generate_overall_analysis_prompt') as mock_prompt, \
             patch('app.interview.improvement_analyzer.call_llm', side_effect=Exception("LLM 서비스 오류")):
            
            mock_prompt.return_value = "테스트 프롬프트"
            
            result = analyze_improvement(
                interview_id=123,
                job_type="백엔드 개발자",
                qa_list=qa_list
            )
            
            assert result["interviewId"] == 123
            assert "분석 중 오류가 발생했습니다" in result["overallComment"]
            assert "LLM 서비스 오류" in result["overallComment"]
    
    def test_analyze_improvement_empty_qa_list(self):
        """빈 Q&A 리스트 테스트"""
        qa_list = []
        mock_llm_response = '{"overallComment": "제공된 질문과 답변이 없어 분석할 수 없습니다."}'
        
        with patch('app.interview.improvement_analyzer.generate_overall_analysis_prompt') as mock_prompt, \
             patch('app.interview.improvement_analyzer.call_llm', return_value=mock_llm_response):
            
            mock_prompt.return_value = "테스트 프롬프트"
            
            result = analyze_improvement(
                interview_id=123,
                job_type="백엔드 개발자",
                qa_list=qa_list
            )
            
            assert result["interviewId"] == 123
            assert result["overallComment"] == "제공된 질문과 답변이 없어 분석할 수 없습니다."
    
    def test_analyze_improvement_multiple_qa_items(self):
        """여러 Q&A 아이템 테스트"""
        qa_list = [
            QAItem(question="자기소개를 해주세요", answer="안녕하세요. 백엔드 개발자입니다."),
            QAItem(question="프로젝트 경험은?", answer="3년간 다양한 프로젝트를 진행했습니다."),
            QAItem(question="기술 스택은?", answer="Python, Django, PostgreSQL을 주로 사용합니다.")
        ]
        mock_llm_response = '{"overallComment": "다양한 질문에 대해 일관성 있게 답변하셨습니다. 특히 기술적 경험을 구체적으로 설명한 점이 인상적입니다."}'
        
        with patch('app.interview.improvement_analyzer.generate_overall_analysis_prompt') as mock_prompt, \
             patch('app.interview.improvement_analyzer.call_llm', return_value=mock_llm_response):
            
            mock_prompt.return_value = "테스트 프롬프트"
            
            result = analyze_improvement(
                interview_id=456,
                job_type="백엔드 개발자",
                qa_list=qa_list
            )
            
            assert result["interviewId"] == 456
            assert "일관성 있게 답변" in result["overallComment"]
            assert "기술적 경험을 구체적으로 설명" in result["overallComment"]
    
    def test_analyze_improvement_json_missing_field(self):
        """JSON 응답에서 필수 필드가 누락된 경우 테스트"""
        qa_list = [QAItem(question="테스트 질문", answer="테스트 답변")]
        mock_llm_response = '{"otherField": "some value"}'  # overallComment 필드 누락
        
        with patch('app.interview.improvement_analyzer.generate_overall_analysis_prompt') as mock_prompt, \
             patch('app.interview.improvement_analyzer.call_llm', return_value=mock_llm_response):
            
            mock_prompt.return_value = "테스트 프롬프트"
            
            result = analyze_improvement(
                interview_id=123,
                job_type="백엔드 개발자",
                qa_list=qa_list
            )
            
            assert result["interviewId"] == 123
            assert result["overallComment"] == "분석을 완료할 수 없습니다."  # 기본값 사용
    
    def test_analyze_improvement_complex_json_response(self):
        """복잡한 JSON 응답 테스트"""
        qa_list = [QAItem(question="테스트 질문", answer="테스트 답변")]
        complex_json = {
            "overallComment": "전체적으로 우수한 면접이었습니다. 강점으로는 기술적 지식의 깊이와 실무 경험의 풍부함이 돋보였습니다. 개선점으로는 답변의 구조화와 구체적인 예시 제시를 더욱 강화하면 좋겠습니다.",
            "strengths": ["기술적 깊이", "실무 경험"],
            "weaknesses": ["답변 구조화", "예시 부족"]
        }
        mock_llm_response = json.dumps(complex_json, ensure_ascii=False)
        
        with patch('app.interview.improvement_analyzer.generate_overall_analysis_prompt') as mock_prompt, \
             patch('app.interview.improvement_analyzer.call_llm', return_value=mock_llm_response):
            
            mock_prompt.return_value = "테스트 프롬프트"
            
            result = analyze_improvement(
                interview_id=123,
                job_type="백엔드 개발자",
                qa_list=qa_list
            )
            
            assert result["interviewId"] == 123
            assert "우수한 면접이었습니다" in result["overallComment"]
            assert "기술적 지식의 깊이" in result["overallComment"]
            assert "답변의 구조화" in result["overallComment"]
