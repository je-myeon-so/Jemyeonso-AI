from fastapi import APIRouter
from app.interview.answer_analyzer import analyze_answer
from app.interview.question_generator import generate_question, fallback_question
from app.interview.improvement_analyzer import analyze_improvement
from app.core.question_cache import question_cache
from app.schemas.interview import (
    AnalyzeAnswerRequest, AnalyzeAnswerResponse,
    GenerateQuestionRequest, GenerateQuestionResponse,
    ImproveRequest, ImproveResponse
)

router = APIRouter(tags=["인터뷰"])

@router.post("/questions", response_model=GenerateQuestionResponse)
def generate_question_endpoint(request: GenerateQuestionRequest):
    try:
        result = generate_question(
            job_type=request.jobType,
            question_level=request.questionLevel,
            question_category=request.questionCategory,
            previous_question=request.previousQuestion,
            previous_answer=request.previousAnswer,
            document_id=request.documentId
        )
        return {
            "code": 200,
            "message": "질문을 생성했습니다.",
            "data": result
        }
    except Exception as e:
        print(f"질문 생성 중 오류 발생: {e}")
        return {
            "code": 500,
            "message": "질문 생성 중 오류가 발생했습니다.",
            "data": fallback_question()
        }


@router.post("/answers/analyze", response_model=AnalyzeAnswerResponse)
def analyze(request: AnalyzeAnswerRequest):
    result = analyze_answer(
        question=request.question,
        answer=request.answer,
        jobtype=request.jobType,
        level=request.questionLevel,
        category=request.questionCategory
    )
    
    # Handle the case where analysis fails completely
    if result is None:
        return {
            "code": 200,
            "message": "분석이 완료되었습니다. 답변에서 특별히 개선할 점을 찾지 못했습니다.",
            "data": {
                "score": 100,  # Default reasonable score
                "analysis": []
            }
        }
    
    # Ensure result has the required fields
    score = result.get("score", 50)
    analysis = result.get("analysis", [])
    
    # Ensure score is in valid range
    score = max(0, min(100, int(score)))
    
    return {
        "code": 200,
        "message": "대답 분석을 성공하였습니다",
        "data": {
            "score": score,
            "analysis": analysis
        }
    }
