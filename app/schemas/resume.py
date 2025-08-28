from pydantic import BaseModel, HttpUrl
from typing import Optional

class ResumeProcessRequest(BaseModel):
    fileUrl: HttpUrl
    userId: int
    documentId: int
    fileType: str

class ResumeParseResponse(BaseModel):
    code: int
    message: str