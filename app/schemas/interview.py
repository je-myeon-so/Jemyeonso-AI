from pydantic import BaseModel
from typing import Optional

# -------- 답변 분석 요청/응답 --------

class AnalyzeAnswerRequest(BaseModel):
    question_category: str
    question_level: str
    jobtype: str
    question: str
    answer: str

class AnswerAnalysisItem(BaseModel):
    error_text: str
    error_type: str
    feedback: str
    suggestion: str

class AnalyzeAnswerResponse(BaseModel):
    code: int
    message: str
    data: dict  # {"analysis.txt": [AnswerAnalysisItem]}

# -------- 꼬리 질문 요청/응답 --------

class FollowUpRequest(BaseModel):
    question_category: str
    question_level: str
    jobtype: str
    previousAnswer: str
    previousQuestion: str

class FollowUpResponse(BaseModel):
    code: int
    message: str
    data: dict  # {"question_type": "꼬리질문", "question": "내용"}

# -------- 질문 생성 요청/응답 --------

class GenerateQuestionRequest(BaseModel):
    question_level: str
    jobtype: str
    question_type: str
    file_id: Optional[str] = None

class GenerateQuestionResponse(BaseModel):
    code: int
    message: str
    data: dict  # {"question": "내용"}