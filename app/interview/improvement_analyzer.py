import json
import re
from typing import List, Dict
from app.core.llm_utils import call_llm
from app.interview.prompt_loader import load_prompt
from app.schemas.interview import QAItem


# 이력서 조회 함수 제거 - 면접 종합 분석에서는 이력서 내용이 불필요
# 면접 답변 자체만으로 종합적인 피드백을 제공하는 것이 목적


def format_qa_list(qa_list: List[QAItem]) -> str:
    """
    Q&A 리스트를 분석용 텍스트로 포맷팅합니다.
    
    Args:
        qa_list (List[QAItem]): Q&A 리스트
        
    Returns:
        str: 포맷팅된 Q&A 텍스트
    """
    formatted_text = ""
    
    for i, qa in enumerate(qa_list, 1):
        formatted_text += f"질문 {i}:\n{qa.question}\n\n답변 {i}:\n{qa.answer}\n\n"
        formatted_text += "-" * 50 + "\n\n"
    
    return formatted_text


def generate_overall_analysis_prompt(
    job_type: str, 
    qa_list: List[QAItem]
) -> str:
    """
    종합 분석을 위한 프롬프트를 생성합니다.
    
    Args:
        job_type (str): 직무 유형
        qa_list (List[QAItem]): Q&A 리스트
        
    Returns:
        str: 생성된 프롬프트
    """
    try:
        # 프롬프트 템플릿 로드
        prompt_template = load_prompt("improvement_analysis.txt")
        
        # Q&A 리스트 포맷팅
        formatted_qa = format_qa_list(qa_list)
        
        # 프롬프트에 변수 치환
        formatted_prompt = prompt_template.format(
            job_type=job_type,
            qa_content=formatted_qa
        )
        
        return formatted_prompt
        
    except FileNotFoundError:
        print("❌ improvement_analysis.txt 프롬프트 파일을 찾을 수 없습니다.")
        # 폴백 프롬프트
        formatted_qa = format_qa_list(qa_list)
        return f"""
당신은 경험이 풍부한 면접관입니다. 지원자의 전체 면접 과정을 종합적으로 분석하여 전체적인 피드백을 제공해주세요.

**직무 유형**: {job_type}

**면접 Q&A 내용**:
{formatted_qa}

다음 JSON 형식으로 응답해주세요:
{{"overallComment": "전체적인 면접 평가와 종합 피드백을 500-800자 내외로 작성해주세요."}}
"""
    except Exception as e:
        print(f"❌ 프롬프트 로드 실패: {e}")
        # 폴백 프롬프트
        formatted_qa = format_qa_list(qa_list)
        return f"""
면접 종합 분석을 수행해주세요.

직무: {job_type}
Q&A: {formatted_qa}

{{"overallComment": "분석 결과를 작성해주세요."}}
"""


def analyze_improvement(
    interview_id: int,
    job_type: str,
    qa_list: List[QAItem]
) -> Dict:
    """
    면접 종합 분석을 수행합니다.
    
    Args:
        interview_id (int): 면접 ID
        job_type (str): 직무 유형
        qa_list (List[QAItem]): Q&A 리스트
        
    Returns:
        Dict: 분석 결과
    """
    try:
        # 프롬프트 생성
        prompt = generate_overall_analysis_prompt(job_type, qa_list)
        
        # LLM 호출
        llm_response = call_llm(
            prompt=prompt,
            temperature=0.3,
            max_tokens=1000,
            system_role="당신은 경험이 풍부한 면접관입니다. 지원자의 전체 면접 과정을 종합적으로 분석하고, 구체적이고 건설적인 피드백을 제공합니다."
        )
        
        # JSON 파싱
        full_response = llm_response.strip()
        json_match = re.search(r'\{[\s\S]*\}', full_response)
        
        if json_match:
            try:
                parsed_response = json.loads(json_match.group(0))
                return {
                    "interviewId": interview_id,
                    "overallComment": parsed_response.get("overallComment", "분석을 완료할 수 없습니다.")
                }
            except json.JSONDecodeError:
                print("❌ JSON 파싱 실패")
                return {
                    "interviewId": interview_id,
                    "overallComment": "분석 결과를 처리하는 중 오류가 발생했습니다. 다시 시도해주세요."
                }
        
        print("❌ JSON 응답 없음")
        return {
            "interviewId": interview_id,
            "overallComment": "분석 결과를 받아올 수 없습니다. 다시 시도해주세요."
        }
        
    except Exception as e:
        print(f"❌ 면접 분석 실패: {e}")
        return {
            "interviewId": interview_id,
            "overallComment": f"분석 중 오류가 발생했습니다: {str(e)}"
        }
