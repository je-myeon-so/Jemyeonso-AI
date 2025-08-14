from openai import OpenAI
from app.config import OPENAI_API_KEY, MODEL_NAME

client = OpenAI(api_key=OPENAI_API_KEY)

def call_llm(prompt: str, temperature: float = 0.7, max_tokens: int = 512, system_role: str = "당신은 면접관입니다.") -> str:
    """
    LLM을 호출하여 응답을 반환합니다.

    Args:
        prompt (str): 사용자 입력 프롬프트
        temperature (float): 출력 다양성 조절 (0.0 ~ 1.5)
        max_tokens (int): 최대 출력 토큰 수
        system_role (str): 시스템 역할 (기본: 면접관)

    Returns:
        str: 모델이 생성한 응답 문자열
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ LLM 호출 실패:", e)
        return "질문 생성 중 오류가 발생했습니다."
