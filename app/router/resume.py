import os
import tempfile
import json
import requests

from fastapi import APIRouter, HTTPException
from app.schemas.resume import ResumeProcessRequest, ResumeParseResponse
from app.resume.parser import extract_text_from_pdf
from app.resume.pii_detector import detect_pii
from app.resume.pii_logger import create_pii_log_payload
from app.core.s3_utils import upload_file_to_s3
from app.core.mysql_utils import update_redacted_resume_content

router = APIRouter(tags=["이력서"])


@router.post("/file/", response_model=ResumeParseResponse)
async def process_resume(request: ResumeProcessRequest):
    """
    S3 URL로 업로드된 이력서를 불러와 텍스트를 추출하고,
    PII 제거 후 DB에 저장하는 엔드포인트.
    """

    # 1. PDF 다운로드
    try:
        pdf_response = requests.get(request.fileUrl)
        pdf_response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF 다운로드 실패: {str(e)}")

    # 2. 임시 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_response.content)
        tmp_path = tmp.name

    # 3. 텍스트 추출
    extracted_text = extract_text_from_pdf(tmp_path)
    os.unlink(tmp_path)

    if not extracted_text:
        raise HTTPException(status_code=400, detail="PDF에서 텍스트를 추출하지 못했습니다.")

    # 4. PII 제거
    pii_result = detect_pii(extracted_text)
    anonymized_text = pii_result["anonymized_text"]

    # 5. DB 업데이트
    success = update_redacted_resume_content(
        document_id=request.documentId,
        redacted_text=anonymized_text
    )

    if not success:
        raise HTTPException(status_code=500, detail="DB 저장 실패")

    # 6. PII 로그 S3 업로드
    pii_payload = create_pii_log_payload(
        user_id=request.userId,
        file_id=str(request.documentId),
        original_filename=f"{request.documentId}.pdf",
        regex_result=pii_result["regex_result"],
        ner_result=pii_result["ner_result"]
    )
    json_bytes = json.dumps(pii_payload, ensure_ascii=False).encode("utf-8")
    object_key = f"pii-logs/{request.documentId}.json"

    upload_file_to_s3(
        file_bytes=json_bytes,
        object_key=object_key,
        content_type="application/json"
    )

    # 7. 성공 응답
    return {
        "code": 200,
        "message": "파일 처리 및 개인정보 삭제가 완료되었습니다"
    }