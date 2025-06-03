from fastapi import APIRouter, Form
from app.resume.pii_detector import detect_pii

router = APIRouter(tags=["개인정보 확인"])

@router.post("/resume/pii-check")
async def check_pii_in_text(text: str = Form(...)):
    result = detect_pii(text)

    return {
        "code": 200,
        "message": "PII 탐지 완료",
        "pii_found": {
            "regex_result": result["regex_result"],
            "ner_result": result["ner_result"]
        },
        "anonymized_text": result["anonymized_text"]
    }