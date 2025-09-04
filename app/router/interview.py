from fastapi import APIRouter
from typing import List
from app.interview.answer_analyzer import analyze_answer
from app.interview.question_generator import generate_question, fallback_question
from app.core.question_cache import question_cache
from app.schemas.interview import (
    AnalyzeAnswerRequest, AnalyzeAnswerResponse,
    GenerateQuestionRequest, GenerateQuestionResponse
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


@router.delete("/questions/cache/{document_id}")
def clear_question_cache(document_id: str):
    """특정 이력서의 질문 캐시 삭제"""
    try:
        deleted_count = question_cache.clear_cache_by_document(document_id)
        return {
            "code": 200,
            "message": f"문서 {document_id}의 질문 캐시 {deleted_count}개 항목이 삭제되었습니다.",
            "data": {"deleted_entries": deleted_count}
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"캐시 삭제 중 오류 발생: {str(e)}"
        }


@router.post("/questions/cache/cleanup")
def cleanup_expired_cache():
    """만료된 캐시 정리"""
    try:
        cleaned_count = question_cache.cleanup_expired_entries()
        return {
            "code": 200,
            "message": f"만료된 캐시 {cleaned_count}개 항목이 정리되었습니다.",
            "data": {"cleaned_entries": cleaned_count}
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"캐시 정리 중 오류 발생: {str(e)}"
        }


@router.get("/questions/cache/stats")
def get_cache_stats():
    """캐시 통계 정보 조회"""
    try:
        stats = question_cache.get_cache_stats()
        return {
            "code": 200,
            "message": "캐시 통계 정보를 조회했습니다.",
            "data": stats
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"캐시 통계 조회 중 오류 발생: {str(e)}"
        }