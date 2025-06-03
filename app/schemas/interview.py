from pydantic import BaseModel
from typing import Optional, List

# -------- 질문 생성 요청/응답 --------

class GenerateQuestionRequest(BaseModel):
    question_level: str
    jobtype: str
    question_category: str
    previous_question: Optional[str] = None
    previous_answer: Optional[str] = None

class QuestionData(BaseModel):
    question_type: str
    question: str

class GenerateQuestionResponse(BaseModel):
    code: int
    message: str
    data: QuestionData

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
    data: List[AnswerAnalysisItem]