from pydantic import BaseModel
from fastapi import UploadFile
from typing import Optional

# 이력서 파일 업로드 요청 스키마
class ResumeUploadRequest(BaseModel):
    file_id: str
    
    class Config:
        arbitrary_types_allowed = True

# 이력서 파일 업로드 응답 스키마
class ResumeUploadResponse(BaseModel):
    code: str
    message: str
    data: Optional[dict] = None 