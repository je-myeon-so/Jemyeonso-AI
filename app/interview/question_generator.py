import random
from typing import Optional, Literal
from app.schemas.interview import QuestionData
from app.interview.prompt_loader import load_prompt
from app.core.llm_utils import call_llm
from app.core.mysql_utils import get_resume_text

QuestionType = Literal["일반질문", "꼬리질문"]

def decide_question_type(previous_question: Optional[str], previous_answer: Optional[str]) -> QuestionType:
    if previous_question is None and previous_answer is None:
        return "일반질문"
    return random.choice(["일반질문", "꼬리질문"])  # TODO: semantic decision later

def fallback_question() -> QuestionData:
    return {
        "question_type": "일반질문",
        "question": "이 직무에 지원하게 된 동기는 무엇인가요?"
    }

def generate_question(question_level: str, job_type: str, question_category: str, previous_question: Optional[str], previous_answer: Optional[str], document_id: Optional[str]) -> QuestionData:
    question_type = decide_question_type(previous_question, previous_answer)
    prompt_file = "question.txt" if question_type == "일반질문" else "follow_up.txt"
    prompt_template = load_prompt(prompt_file)

    if question_type == "일반질문":
        if not document_id:
            raise ValueError("일반질문 생성을 위해 document_id가 필요합니다.")
        resume_text = get_resume_text(document_id)
        if not resume_text:
            raise ValueError("이력서 내용을 찾을 수 없습니다.")
        prompt = prompt_template.format(
            resume_text=resume_text,
            question_level=question_level,
            job_type=job_type,
            question_category=question_category,
            question_type=question_type
        )
    else:
        prompt = prompt_template.format(
            previousQuestion=previous_question or "",
            previousAnswer=previous_answer or "",
            question_level=question_level,
            job_type=job_type,
            question_category=question_category,
            question_type=question_type
        )

    try:
        response = call_llm(
            prompt,
            temperature=0.6 if question_type == "일반질문" else 0.8,
            max_tokens=512
        )

        return {
            "question_type": question_type,
            "question": response.strip() if isinstance(response, str) else str(response)
        }

    except Exception as e:
        print("❌ 질문 생성 실패:", e)
        return fallback_question()