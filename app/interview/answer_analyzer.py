import json
import re
from app.interview.prompt_loader import load_prompt
from app.core.llm_utils import call_llm
from app.core.wikipedia_service import WikipediaService

MAX_CONCEPTS_TO_PROCESS = 3
WIKIPEDIA_EXTRACT_TRUNCATE_LENGTH = 300


def extract_technical_concepts(answer: str, jobtype: str) -> list:
    try:
        prompt_template = load_prompt("concept_extraction.txt")
        prompt = prompt_template.format(answer=answer, job_type=jobtype)
    except FileNotFoundError:
        return []
    except (AttributeError, KeyError, TypeError):
        return []

    try:
        response = call_llm(
            prompt=prompt,
            temperature=0.1,
            max_tokens=200,
            system_role="당신은 기술 면접 전문가입니다. 답변에서 검증 가능한 기술 개념을 정확히 추출합니다."
        )
        concepts = json.loads(response.strip())
        return concepts if isinstance(concepts, list) else []
    except (json.JSONDecodeError, ValueError, TypeError, Exception):
        return []


def get_wikipedia_context(concepts: list) -> str:
    if not concepts:
        return ""

    wikipedia_service = WikipediaService()
    fact_context = "\n\n**기술적 정확성 검증을 위한 참고 정보:**\n"

    for concept in concepts[:MAX_CONCEPTS_TO_PROCESS]:
        wiki_data = wikipedia_service.get_concept_summary(concept)
        if not wiki_data:
            search_title = wikipedia_service.search_concept(concept)
            if search_title:
                wiki_data = wikipedia_service.get_concept_summary(search_title)

        if wiki_data and wiki_data.get("extract"):
            extract = wiki_data["extract"][:WIKIPEDIA_EXTRACT_TRUNCATE_LENGTH]
            fact_context += f"- **{concept}**: {extract}...\n"

    fact_context += "\n위 정보를 참고하여 답변의 기술적 정확성도 함께 평가해주세요. 잘못된 설명이 있다면 '전문성 부족' 유형으로 분류하고 정확한 정보를 제공해주세요.\n"
    return fact_context


def analyze_answer(question: str, answer: str, jobtype: str, level: str, category: str) -> dict:
    technical_concepts = extract_technical_concepts(answer, jobtype)
    wikipedia_context = get_wikipedia_context(technical_concepts)

    prompt_template = load_prompt("analysis.txt")
    formatted_prompt = prompt_template.format(
        question=question.strip(),
        text=answer.strip(),
        jobtype=jobtype,
        level=level,
        category=category
    )
    prompt = formatted_prompt + wikipedia_context
    try:
        llm_response = call_llm(
            prompt=prompt,
            temperature=0.3,
            max_tokens=512,
            system_role="당신은 경험이 풍부한 면접관입니다. 지원자의 답변을 분석하고, 면접자의 입장에서 구체적인 피드백을 제공합니다."
        )
    except (ConnectionError, TimeoutError, ValueError) as e:
        print("❌ LLM 호출 실패:", e)
        return None

    full_response = llm_response.strip()
    json_match = re.search(r'\{[\s\S]*\}', full_response)

    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            print("❌ JSON 파싱 실패")
            return None

    print("❌ JSON 응답 없음")
    return None
