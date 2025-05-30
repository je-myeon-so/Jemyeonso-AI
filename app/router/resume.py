from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.resume import ResumeUploadRequest, ResumeUploadResponse
from app.resume.parser import file_extract
from app.core.mysql_utils import insert_one
from typing import Optional

router = APIRouter(
    tags=["이력서"]
)

@router.post("/file/", response_model=ResumeUploadResponse)
async def upload_resume(
    file_id: str = Form(...),
    file: UploadFile = File(...)
):
    # 파일 확장자 확인
    if not file.filename.lower().endswith('.pdf'):
        return JSONResponse(
            status_code=200,
            content={
                "code": "200", 
                "message": "PDF 파일만 업로드 가능합니다.",
                "data": None
            }
        )
    
    # PDF에서 텍스트 추출
    extracted_text = await file_extract(file)
    
    # 텍스트 추출 성공 여부 확인
    if extracted_text is None:
        return JSONResponse(
            status_code=200,
            content={
                "code": "200", 
                "message": "텍스트 추출에 실패했습니다.",
                "data": None
            }
        )
    
    # 추출한 텍스트를 DB에 저장
    try:
        query = """
        INSERT INTO resumes (file_id, resume_text) 
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE resume_text = %s
        """
        success = insert_one(query, (file_id, extracted_text, extracted_text))
        
        if not success:
            return JSONResponse(
                status_code=200,
                content={
                    "code": "200",
                    "message": "텍스트 저장에 실패했습니다.",
                    "data": None
                }
            )
    except Exception as e:
        print(f"DB 저장 오류: {e}")
        return JSONResponse(
            status_code=200,
            content={
                "code": "200",
                "message": "텍스트 저장 중 오류가 발생했습니다.",
                "data": None
            }
        )
    
    return JSONResponse(
        status_code=200,
        content={
            "code": "200",
            "message": "파일 업로드 및 개인 정보 삭제를 성공했습니다",
            "data": None
        }
    ) 