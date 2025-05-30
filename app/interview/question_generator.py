from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME
from app.interview.prompt_loader import load_prompt
from app.core.mysql_utils import fetch_one
import json

client = OpenAI(api_key=OPENAI_API_KEY)

def get_resume_text(file_id: str) -> str:
    """
    파일 ID를 기반으로 DB에서 이력서 텍스트를 가져옵니다.
    실제 DB 연동 코드로 대체해야 합니다.
    """
    # 임시 구현: 실제로는 DB에서 조회하는 로직으로 변경 필요
    query = "SELECT resume_text FROM resumes WHERE file_id = %s"
    result = fetch_one(query, (file_id,))
    
    if result and 'resume_text' in result:
        return result['resume_text']
    
    # 실제 환경에서는 에러 처리 필요
    return "이력서 내용을 찾을 수 없습니다."

def generate_question(job_type: str, level: str, category: str, question_type: str, file_id: str = None) -> dict:
    """
    이력서 내용을 기반으로 면접 질문을 생성합니다.
    
    Args:
        job_type: 직무 유형 (예: "백엔드 개발자", "프론트엔드 개발자")
        level: 난이도 (예: "초급", "중급", "고급")
        category: 면접 카테고리 (예: "기술", "인성", "직무")
        question_type: 질문 유형 (예: "기술", "경험", "상황")
        file_id: 이력서 파일 ID
        
    Returns:
        dict: 생성된 질문 정보
    """
    # 이력서 텍스트 가져오기
    resume_text = get_resume_text(file_id) if file_id else "이력서 내용이 제공되지 않았습니다."
    
    # 프롬프트 불러오기 및 변수 삽입
    prompt_template = load_prompt("question.txt")
    prompt = prompt_template.format(
        job_type=job_type,
        level=level,
        category=category,
        question_type=question_type,
        resume_text=resume_text
    )
    
    # GPT 호출
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "당신은 경험이 풍부한 면접관입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # 응답에서 질문 추출
    question_text = response.choices[0].message.content.strip()
    
    return {
        "question": question_text
    }
