from fastapi import APIRouter
from app.interview.answer_analyzer import analyze_answer
from app.interview.follow_up_generator import generate_follow_up
from app.schemas.interview import AnalyzeAnswerRequest, AnalyzeAnswerResponse, FollowUpRequest, FollowUpResponse
router = APIRouter( tags=["인터뷰"])

#개발자 바꿔야됨

@router.post("/answers/analyze", response_model=AnalyzeAnswerResponse)
async def analyze(request: AnalyzeAnswerRequest):
    result = analyze_answer(
        question=request.question,
        answer=request.answer,
        job_role=request.jobtype  # jobtype → 내부 함수에 전달
    )
    return {
        "code": 200,
        "message": "대답 분석을 성공하였습니다",
        "data": result["analysis_result"]
    }

@router.post("/questions/followup", response_model=FollowUpResponse)
async def follow_up(request: FollowUpRequest):
    followup = generate_follow_up(
        answer=request.previousAnswer,
        question=request.previousQuestion,
        job_role=request.jobtype  # jobtype → 내부 함수에 전달
    )
    return {
        "code": 200,
        "message": "꼬리질문을 생성했습니다.",
        "data": followup["question"]
    }
