import json
import re
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME
from app.interview.prompt_loader import load_prompt

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_follow_up(answer: str, question: str, job_role: str) -> dict:
    prompt_template = load_prompt("follow_up")
    prompt = prompt_template.format(answer=answer.strip(), question=question, job_role=job_role)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "당신은 면접 질문 생성 전문가입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    full_response = response.choices[0].message.content.strip()
    json_match = re.search(r'\{[\s\S]*\}', full_response)

    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            return fallback_question()
    return fallback_question()


def fallback_question():
    return {
        "question": {
            "questiontext": "이 직무에 지원하게 된 동기는 무엇인가요?",
            "questiontype": "꼬리질문"
        }
    }