from pydantic import BaseModel, HttpUrl
from typing import Optional

class ResumeProcessRequest(BaseModel):
    file_url: HttpUrl
    user_id: int
    document_id: int
    file_type: str

class ResumeParseResponse(BaseModel):
    code: int
    message: str