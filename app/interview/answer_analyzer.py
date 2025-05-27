import json
import re
from kiwipiepy import Kiwi
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME
from app.interview.prompt_loader import load_prompt

client = OpenAI(api_key=OPENAI_API_KEY)
kiwi = Kiwi()


def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def analyze_text(text: str, question: str, job_role: str) -> dict:
    prompt_template = load_prompt("analysis")
    prompt = prompt_template.format(text=text, question=question, job_role=job_role)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "당신은 경험 많은 면접관입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    full_response = response.choices[0].message.content.strip()
    json_match = re.search(r'\{[\s\S]*\}', full_response)

    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            return {"error": "JSON 파싱 실패", "raw_output": full_response}
    return {"error": "JSON 형식 없음", "raw_output": full_response}


def analyze_answer(question: str, answer: str, job_role: str) -> dict:
    cleaned = clean_text(answer)
    return {
        "original_answer": answer,
        "analysis_result": analyze_text(cleaned, question, job_role)
    }
