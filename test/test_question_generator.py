import pytest
from app.interview.question_generator import decide_question_type, generate_questions, fallback_question

def test_decide_question_type():
    """이전 질문이 없으면 '일반질문'을, 있으면 둘 중 하나를 반환하는지 테스트"""
    # 첫 질문일 경우
    assert decide_question_type(None, None) == "일반질문"

    # 이전 질문/답변이 있는 경우 (랜덤이므로 여러 번 테스트하여 확인)
    results = {decide_question_type("질문1", "답변1") for _ in range(20)}
    assert "일반질문" in results
    assert "꼬리질문" in results

def test_generate_questions():
    """이전 질문 리스트를 올바른 포맷의 문자열로 변환하는지 테스트"""
    # 이전 질문이 있을 경우
    questions = ["질문1", "질문2"]
    expected_text = """
**이전에 생성된 질문들 (중복 금지):**
- 질문1
- 질문2

위 질문들과 겹치지 않는 새로운 관점의 질문을 생성하세요.
"""
    assert generate_questions(questions) == expected_text

    # 이전 질문이 없을 경우
    assert generate_questions([]) == ""

def test_fallback_question():
    """대체 질문이 올바른 형식으로 반환되는지 테스트"""
    question_data = fallback_question()
    assert "questionType" in question_data
    assert "question" in question_data
    assert question_data["questionType"] == "일반질문"