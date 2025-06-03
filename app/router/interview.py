from fastapi import APIRouter
from app.interview.answer_analyzer import analyze_answer
from app.interview.follow_up_generator import generate_follow_up
from app.schemas.interview import AnalyzeAnswerRequest, AnalyzeAnswerResponse, FollowUpRequest, FollowUpResponse
router = APIRouter( tags=["인터뷰"])

@router.post("/answers/analyze", response_model=AnalyzeAnswerResponse)
def analyze(request: AnalyzeAnswerRequest):
    result = analyze_answer(
        question=request.question,
        answer=request.answer,
        jobtype=request.jobtype,
        level=request.question_level,
        category=request.question_category
    )
    return result

@router.post("/questions/followup", response_model=FollowUpResponse)
def follow_up(request: FollowUpRequest):
    result = generate_follow_up(
        answer=request.previousAnswer,
        question=request.previousQuestion,
        jobtype=request.jobtype,
        level=request.question_level,
        category=request.question_category
    )
    return result