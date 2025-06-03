from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.resume import ResumeUploadRequest, ResumeUploadResponse
from app.resume.parser import file_extract
from app.core.mysql_utils import insert_one
from app.resume.pii_detector import detect_pii
from app.resume.pii_logger import create_pii_log_payload
from app.core.s3_utils import upload_file_to_s3
from typing import Optional
import json

router = APIRouter(
    tags=["이력서"]
)


@router.post("/file/", response_model=ResumeUploadResponse)
async def upload_resume(
        file_id: str = Form(...),
        file: UploadFile = File(...),
        user_id: str = Form(...)
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

    # 개인정보 검출 및 익명화
    pii_result = detect_pii(extracted_text)
    anonymized_text = pii_result["anonymized_text"]

    # PII 로그 생성
    pii_payload = create_pii_log_payload(
        user_id=user_id,
        file_id=file_id,
        original_filename=file.filename,
        regex_result=pii_result["regex_result"],
        ner_result=pii_result["ner_result"]
    )

    # S3에 PII 로그 업로드
    json_bytes = json.dumps(pii_payload, ensure_ascii=False).encode("utf-8")
    object_key = f"pii-logs/{file_id}.json"

    upload_success = upload_file_to_s3(
        file_bytes=json_bytes,
        object_key=object_key,
        content_type="application/json"
    )

    # 익명화된 텍스트를 DB에 저장
    try:
        query = """
                INSERT INTO resumes (file_id, resume_text)
                VALUES (%s, %s) ON DUPLICATE KEY \
                UPDATE resume_text = %s \
                """
        success = insert_one(query, (file_id, anonymized_text, anonymized_text))

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

# 개인정보 관련 API 엔드포인트

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