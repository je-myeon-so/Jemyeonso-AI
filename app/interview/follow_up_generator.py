import json
import re
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME
from app.interview.prompt_loader import load_prompt

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_follow_up(question: str, answer: str, jobtype: str, level: str, category: str) -> dict:
    prompt_template = load_prompt("follow_up.txt")
    prompt = prompt_template.format(
        answer=answer.strip(),
        question=question.strip(),
        jobtype=jobtype,
        level=level,
        category=category
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "당신은 면접 질문 생성 전문가입니다."},
            {"role": "user", "content": prompt}
        ]
    )

    full_response = response.choices[0].message.content.strip()
    json_match = re.search(r'\{[\s\S]*?\}', full_response)  # 최소 매칭으로 수정
    # print("GPT 응답 원본:\n", full_response)

    if json_match:
        try:
            parsed = json.loads(json_match.group(0))
            if "question" in parsed:
                return {
                    "code": 200,
                    "message": "꼬리질문 생성 완료",
                    "data": parsed
                }
        except json.JSONDecodeError:
            pass

    return fallback_question()


def fallback_question():
    return {
        "code": 200,
        "message": "꼬리질문 생성 실패, 기본 질문 반환",
        "data": {
            "question": "이 직무에 지원하게 된 동기는 무엇인가요?"
        }
    }