from pydantic import BaseModel

# -------- 답변 분석 요청/응답 --------

class AnalyzeAnswerRequest(BaseModel):
    question: str
    answer: str
    jobtype: str
    category: str

class AnswerAnalysisItem(BaseModel):
    error_text: str
    error_type: str
    feedback: str
    suggestion: str

class AnalyzeAnswerResponse(BaseModel):
    code: int
    message: str
    data: dict  # {"analysis": [AnswerAnalysisItem]}

# -------- 꼬리 질문 요청/응답 --------

class FollowUpRequest(BaseModel):
    previousAnswer: str
    previousQuestion: str
    jobtype: str
    category: str

class FollowUpResponse(BaseModel):
    code: int
    message: str
    data: dict  # {"question_type": "꼬리질문", "question": "내용"}