from fastapi import APIRouter
from typing import List
from app.interview.answer_analyzer import analyze_answer
from app.interview.question_generator import generate_question
from app.schemas.interview import (
    AnalyzeAnswerRequest, AnalyzeAnswerResponse,
    GenerateQuestionRequest, GenerateQuestionResponse
)

router = APIRouter(tags=["인터뷰"])

@router.post("/questions", response_model=GenerateQuestionResponse)
def generate_question_endpoint(request: GenerateQuestionRequest):
    try:
        result = generate_question(
            job_type=request.jobtype,
            question_level=request.question_level,
            question_category=request.question_category,
            previous_question=request.previous_question,
            previous_answer=request.previous_answer
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
def analyze(request: AnalyzeAnswerRequest):
    result = analyze_answer(
        question=request.question,
        answer=request.answer,
        jobtype=request.jobtype,
        level=request.question_level,
        category=request.question_category
    )
    return {
        "code": 200,
        "message": "대답 분석을 성공하였습니다",
        "data": result
    }