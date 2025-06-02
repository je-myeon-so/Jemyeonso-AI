from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any

def create_pii_log_payload(user_id: str, file_id: str, original_filename: str, regex_result: Dict[str, List[str]], ner_result: Dict[str, List[str]]) -> Dict[str, Any]:
    now = datetime.now(timezone(timedelta(hours=9))).isoformat()

    regex_keys = set(regex_result.keys())
    ner_keys = set(ner_result.keys())
    all_detected_keys = sorted(regex_keys.union(ner_keys))

    log_payload = {
        "code": "200",
        "message": "파일 업로드 및 개인 정보 삭제를 성공했습니다",
        "data": {
            "deleted_at": now,
            "deleted_by": "AI_SERVER",
            "user_id": user_id,
            "file_id": file_id,
            "detected_pii_fields": all_detected_keys,
            "deleted_fields": all_detected_keys,
            "deletion_method": "anonymization",
            "deletion_reason": "policy_auto",
            "deletion_status": "success",
            "validation_result": "no remaining PII",
            "original_filename": original_filename
        }
    }

    return log_payload