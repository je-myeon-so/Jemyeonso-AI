import random
from typing import Optional, Literal
from app.schemas.interview import QuestionData
from app.interview.prompt_loader import load_prompt
from app.core.llm_utils import call_llm
from app.core.mysql_utils import get_resume_text
from app.core.question_cache import question_cache
from app.rag.rag_service import rag_service

QuestionType = Literal["일반질문", "꼬리질문"]

def decide_question_type(previous_question: Optional[str], previous_answer: Optional[str]) -> QuestionType:
    """질문 타입 결정 (일반질문 vs 꼬리질문)"""
    if previous_question is None and previous_answer is None:
        return "일반질문"
    return random.choice(["일반질문", "꼬리질문"])  # TODO: semantic decision later

def fallback_question() -> QuestionData:
    """질문 생성 실패 시 대체 질문 반환"""
    return {
        "questionType": "일반질문",
        "question": "이 직무에 지원하게 된 동기는 무엇인가요?"
    }

def generate_questions(previous_questions: list[str]) -> str:
    """이전 질문들을 프롬프트에 포함할 형식으로 변환"""
    if not previous_questions:
        return ""
    
    questions_text = "\n".join([f"- {q}" for q in previous_questions])
    return f"""
**이전에 생성된 질문들 (중복 금지):**
{questions_text}

위 질문들과 겹치지 않는 새로운 관점의 질문을 생성하세요.
"""

def generate_question(question_level: str, job_type: str, question_category: str, 
                     previous_question: Optional[str], previous_answer: Optional[str], 
                     document_id: Optional[str]) -> QuestionData:
    """면접 질문 생성 (RAG 기반 CultureFit 분기 + 기존 로직, 중복 방지 포함)"""

    # 이력서 내용 (CultureFit 또는 일반질문 시 필요)
    resume_text: Optional[str] = None
    if document_id:
        resume_text = get_resume_text(document_id)
        if not resume_text:
            raise ValueError("이력서 내용을 찾을 수 없습니다.")

    # --- RAG 기반 CultureFit 질문 생성 ---
    if question_category == "CultureFit":
        if not resume_text:
            raise ValueError("CultureFit 질문 생성을 위해 document_id와 이력서 내용이 필요합니다.")
        try:
            context = rag_service.get_culturefit_context(resume_text)
            prompt_template = load_prompt("culturefit.txt")
            prompt = prompt_template.format(
                context=context,
                resume_text=resume_text,
                job_type=job_type,
                question_level=question_level,
                question_category=question_category,
                previous_questions_section=previous_questions_section,
            )
            response = call_llm(
                prompt,
                temperature=0.8,
                max_tokens=512,
            )
            generated_question = response.strip() if isinstance(response, str) else str(response)
            return {
                "questionType": "일반질문",
                "question": generated_question,
            }
        except Exception as e:
            print(f"❌ RAG 질문 생성 실패: {e}")
            return fallback_question()

    # --- 기존 질문 생성 로직 (일반질문, 꼬리질문) ---
    question_type = decide_question_type(previous_question, previous_answer)
    prompt_file = "question.txt" if question_type == "일반질문" else "follow_up.txt"
    prompt_template = load_prompt(prompt_file)

    if question_type == "일반질문":
        if not document_id:
            raise ValueError("일반질문 생성을 위해 document_id가 필요합니다.")

        previous_questions = question_cache.get_previous_questions(
            document_id, job_type, question_category, question_level
        )

        previous_questions_section = generate_questions(previous_questions)

        if resume_text is None:
            raise ValueError("이력서 내용을 찾을 수 없습니다.")

        prompt = prompt_template.format(
            resume_text=resume_text,
            question_level=question_level,
            job_type=job_type,
            question_category=question_category,
            question_type=question_type,
            previous_questions_section=previous_questions_section,
        )
    else:
        prompt = prompt_template.format(
            previousQuestion=previous_question or "",
            previousAnswer=previous_answer or "",
            question_level=question_level,
            job_type=job_type,
            question_category=question_category,
            question_type=question_type,
        )

    try:
        response = call_llm(
            prompt,
            temperature=0.8,
            max_tokens=512,
        )

        generated_question = response.strip() if isinstance(response, str) else str(response)

        if question_type == "일반질문" and document_id:
            question_cache.add_question(
                document_id, job_type, question_category, question_level, generated_question
            )

        return {
            "questionType": question_type,
            "question": generated_question,
        }
    except Exception as e:
        print("❌ 질문 생성 실패:", e)
        return fallback_question()