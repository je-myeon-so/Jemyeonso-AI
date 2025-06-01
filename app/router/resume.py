from fastapi import APIRouter, Form
from app.resume.pii_detector import detect_pii
from app.resume.pii_logger import create_pii_log_payload
from app.core.s3_utils import upload_file_to_s3
import json

router = APIRouter(tags=["개인정보 삭제"])

# JSON만 생성해서 반환
@router.post("/resume/pii-log")
async def generate_pii_log_json(
    user_id: str = Form(...),
    file_id: str = Form(...),
    original_filename: str = Form(...),
    text: str = Form(...)
):
    result = detect_pii(text)
    payload = create_pii_log_payload(
        user_id=user_id,
        file_id=file_id,
        original_filename=original_filename,
        regex_result=result["regex_result"],
        ner_result=result["ner_result"]
    )

    return {
        "code": 200,
        "message": "PII 로그 JSON 생성 완료",
        "log": payload,
        "anonymized_text": result["anonymized_text"]
    }

# S3에 JSON 파일 업로드까지 수행
@router.post("/resume/pii-upload")
async def delete_pii_and_upload_log(
    user_id: str = Form(...),
    file_id: str = Form(...),
    original_filename: str = Form(...),
    text: str = Form(...)
):
    result = detect_pii(text)
    payload = create_pii_log_payload(
        user_id=user_id,
        file_id=file_id,
        original_filename=original_filename,
        regex_result=result["regex_result"],
        ner_result=result["ner_result"]
    )

    # S3 업로드용 JSON 직렬화 및 바이트 변환
    json_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    object_key = f"pii-logs/{file_id}.json"

    upload_success = upload_file_to_s3(
        file_bytes=json_bytes,
        object_key=object_key,
        content_type="application/json"
    )

    return {
        "code": 200 if upload_success else 500,
        "message": "PII 로그 업로드 완료" if upload_success else "PII 로그 업로드 실패",
        "anonymized_text": result["anonymized_text"]
    }