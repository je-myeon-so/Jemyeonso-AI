import random
from typing import Optional, Literal
from app.interview.prompt_loader import load_prompt
from app.core.llm_utils import call_llm

QuestionType = Literal["일반질문", "꼬리질문"]

def decide_question_type(previous_question: Optional[str], previous_answer: Optional[str]) -> QuestionType:
    """
    현재는 랜덤 기반 질문 타입 결정. 이후 의미 기반으로 교체 가능.
    """
    if previous_question is None and previous_answer is None:
        return "일반질문"
    return random.choice(["일반질문", "꼬리질문"])  # TODO: 향후 semantic 판단으로 교체


def fallback_question() -> dict:
    """
    질문 생성 실패 시 기본 질문 반환
    """
    return {
        "question_type": "일반질문",
        "question": "이 직무에 지원하게 된 동기는 무엇인가요?"
    }

def generate_question(question_level: str, job_type: str, question_category: str, previous_question: Optional[str], previous_answer: Optional[str]) -> dict:
    """
    질문을 생성하여 {question_type, question} 형태로 반환
    """
    question_type = decide_question_type(previous_question, previous_answer)
    prompt_file = "question.txt" if question_type == "일반질문" else "follow_up.txt"
    prompt_template = load_prompt(prompt_file)

    prompt = prompt_template.format(
        level=question_level,
        jobtype=job_type,
        category=question_category,
        previousQuestion=previous_question or "",
        previousAnswer=previous_answer or ""
    )

    try:
        response = call_llm(
            prompt,
            temperature=0.7 if question_type == "일반질문" else 0.8,
            max_tokens=512
        )

        return {
            "question_type": question_type,
            "question": response
        }

    except Exception as e:
        print("❌ 질문 생성 실패:", e)
        return fallback_question()