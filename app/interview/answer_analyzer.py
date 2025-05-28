import json
import re
from openai import OpenAI
from kiwipiepy import Kiwi
from config import OPENAI_API_KEY, MODEL_NAME
from app.interview.prompt_loader import load_prompt
from app.core.mysql_utils import get_context  # 인터뷰 컨텍스트 가져오는 함수
from pprint import pprint

client = OpenAI(api_key=OPENAI_API_KEY)
kiwi = Kiwi()


def analyze_answer(question: str, answer: str, job_role: str, level: str, category: str) -> dict:
    # 프롬프트 불러오기 및 변수 삽입
    prompt_template = load_prompt("analysis.txt")
    prompt = prompt_template.format(
        question=question.strip(),
        text=answer.strip(),
        job_role=job_role,
        level=level,
        category=category
    )

    # GPT 호출
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "당신은 경험이 풍부한 면접관입니다. 지원자의 답변을 분석하고, 면접자의 입장에서 구체적인 피드백을 제공합니다."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # 응답 파싱
    full_response = response.choices[0].message.content.strip()
    json_match = re.search(r'\{[\s\S]*\}', full_response)

    if json_match:
        try:
            analysis_result = json.loads(json_match.group(0))
            return {
                "original_answer": answer,
                "analysis_result": analysis_result
            }
        except json.JSONDecodeError:
            return {
                "original_answer": answer,
                "analysis_result": {
                    "error": "모델이 유효한 JSON을 생성하지 않았습니다.",
                    "raw_output": full_response
                }
            }

    return {
        "original_answer": answer,
        "analysis_result": {
            "error": "모델 응답에서 JSON 데이터를 찾을 수 없습니다.",
            "raw_output": full_response
        }
    }


# 로컬 테스트용
if __name__ == "__main__":
    interview_id = 1  # 존재하는 인터뷰 ID로 변경하세요
    context = get_context(interview_id)

    if not context:
        print("❌ 인터뷰 컨텍스트를 불러오지 못했습니다.")
    else:
        question = "자신의 강점을 말해주세요."
        answer = "어.. 저는 음.. 새로운 환경에서도 빠르게 적응할 수 있습니다. API 최적화 경험도 있습니다."

        jobtype = context["job_type"]
        level = context["question_level"]
        category = context["question_type"]

        result = analyze_answer(question, answer, jobtype, level, category)
        pprint(result)