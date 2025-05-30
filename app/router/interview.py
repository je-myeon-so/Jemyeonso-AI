from fastapi import APIRouter
from app.interview.answer_analyzer import analyze_answer
from app.interview.follow_up_generator import generate_follow_up
from app.interview.question_generator import generate_question
from app.schemas.interview import (
    AnalyzeAnswerRequest, AnalyzeAnswerResponse, 
    FollowUpRequest, FollowUpResponse,
    GenerateQuestionRequest, GenerateQuestionResponse
)
from app.core.mysql_utils import get_context
router = APIRouter(tags=["인터뷰"])

@router.post("/questions", response_model=GenerateQuestionResponse)
def generate_question_endpoint(request: GenerateQuestionRequest):
    try:
        result = generate_question(
            job_type=request.jobtype,
            level=request.level,
            category=request.category,
            question_type=request.question_type,
            file_id=request.file_id
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
            "data": None
        }

@router.post("/answers/analyze", response_model=AnalyzeAnswerResponse)
def analyze(payload: AnalyzeAnswerRequest):
    context = get_context(payload.interview_id)
    if context is None:
        return {
            "code": 500,
            "message": "인터뷰 컨텍스트 조회 실패",
            "data": None
        }

    result = analyze_answer(
        question=payload.question,
        answer=payload.answer,
        job_role=context["job_type"],
        level=context["question_level"],
        category=context["question_type"]
    )

    return {
        "code": 200,
        "message": "대답 분석을 성공하였습니다",
        "data": result
    }

@router.post("/questions/followup", response_model=FollowUpResponse)
def follow_up_endpoint(request: FollowUpRequest):
    context = get_context(request.interview_id)
    if context is None:
        return {
            "code": 500,
            "message": "인터뷰 컨텍스트 조회 실패",
            "data": None
        }

    result = generate_follow_up(
        answer=request.previousAnswer,
        question=request.previousQuestion,
        job_role=context["job_type"],
        level=context["question_level"],
        category=context["question_type"]
    )
    return {
        "code": 200,
        "message": "꼬리질문을 생성했습니다.",
        "data": result
    }