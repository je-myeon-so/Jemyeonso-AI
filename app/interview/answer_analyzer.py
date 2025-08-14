import json
import re
from app.interview.prompt_loader import load_prompt
from app.core.llm_utils import call_llm

def analyze_answer(question: str, answer: str, jobtype: str, level: str, category: str) -> dict:
    """
    면접 답변을 분석하여 JSON 형태의 분석 결과만 반환합니다.
    실패 시 None 반환
    """
    prompt_template = load_prompt("analysis.txt")
    prompt = prompt_template.format(
        question=question.strip(),
        text=answer.strip(),
        jobtype=jobtype,
        level=level,
        category=category
    )
    try:
        llm_response = call_llm(
            prompt=prompt,
            temperature=0.3,
            max_tokens=512,
            system_role="당신은 경험이 풍부한 면접관입니다. 지원자의 답변을 분석하고, 면접자의 입장에서 구체적인 피드백을 제공합니다."
        )
    except Exception as e:
        print("❌ LLM 호출 실패:", e)
        return None

    # JSON 추출 시도
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
