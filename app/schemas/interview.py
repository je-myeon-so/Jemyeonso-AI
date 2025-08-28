from pydantic import BaseModel
from typing import Optional, List

# -------- 질문 생성 요청/응답 --------

class GenerateQuestionRequest(BaseModel):
    questionLevel: str
    jobType: str
    questionCategory: str
    previousQuestion: Optional[str] = None
    previousAnswer: Optional[str] = None
    documentId: Optional[int] = None

class QuestionData(BaseModel):
    questionType: str
    question: str

class GenerateQuestionResponse(BaseModel):
    code: int
    message: str
    data: QuestionData

# -------- 답변 분석 요청/응답 --------

class AnalyzeAnswerRequest(BaseModel):
    questionCategory: str
    questionLevel: str
    jobType: str
    question: str
    answer: str

class AnswerAnalysisItem(BaseModel):
    errorText: str
    errorType: str
    feedback: str
    suggestion: str

class AnalyzeAnswerData(BaseModel):
    analysis: List[AnswerAnalysisItem]

class AnalyzeAnswerResponse(BaseModel):
    code: int
    message: str
    data: AnalyzeAnswerData