from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME
from app.interview.prompt_loader import load_prompt
from app.core.mysql_utils import fetch_one
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

def get_resume_text(file_id: str) -> str:
    """
    파일 ID를 기반으로 DB에서 이력서 텍스트를 가져옵니다.
    """
    try:
        query = "SELECT resume_text FROM resumes WHERE file_id = %s"
        result = fetch_one(query, (file_id,))
        
        if result and 'resume_text' in result and result['resume_text']:
            return result['resume_text']
        
        logger.warning(f"이력서를 찾을 수 없음 (file_id: {file_id})")
        return "이력서 내용을 찾을 수 없습니다. 유효한 이력서 ID를 확인해주세요."
    except Exception as e:
        logger.error(f"이력서 조회 중 오류 발생: {str(e)}")
        return f"이력서 조회 중 오류가 발생했습니다: {str(e)}"

def generate_question(job_type: str, question_level: str, question_type: str, file_id: str = None) -> dict:
    """
    이력서 내용을 기반으로 면접 질문을 생성합니다.
    
    Args:
        job_type: 직무 유형 (예: "백엔드 개발자", "프론트엔드 개발자")
        question_level: 난이도 (예: "초급", "중급", "고급")
        question_type: 질문 유형 (예: "느슨", "압박", "기술")
        file_id: 이력서 파일 ID
        
    Returns:
        dict: 생성된 질문 정보
    """
    try:
        # 이력서 텍스트 가져오기
        resume_text = get_resume_text(file_id) if file_id else "이력서 내용이 제공되지 않았습니다."
        
        # 프롬프트 불러오기 및 변수 삽입
        prompt_template = load_prompt("question.txt")
        prompt = prompt_template.format(
            job_type=job_type,
            question_level=question_level,
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
    except Exception as e:
        logger.error(f"질문 생성 중 오류 발생: {str(e)}")
        return {
            "question": "질문 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            "error": str(e)
        }
