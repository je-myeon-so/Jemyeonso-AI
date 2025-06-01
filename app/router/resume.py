from fastapi import APIRouter, UploadFile, Form, File
from app.resume.pii_detector import detect_pii
from app.resume.pii_logger import log_pii_deletion

router = APIRouter(tags=["개인정보 삭제"])

@router.post("/resume/analyze")
async def analyze_resume(user_id: str = Form(...), file_id: str = Form(...), original_filename: str = Form(...), text: str = Form(...)):
    result = detect_pii(text)
    log_pii_deletion(
        user_id=user_id,
        file_id=file_id,
        original_filename=original_filename,
        detected_fields=result["detected_pii_fields"],
        deleted_fields=result["deleted_fields"]
    )
    return {
        "code": 200,
        "message": "PII 탐지 및 삭제 완료",
        "anonymized_text": result["anonymized_text"]
    }