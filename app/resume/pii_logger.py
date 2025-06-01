import json
from datetime import datetime, timezone, timedelta
from app.core.mysql_utils import insert_one

def log_pii_deletion(user_id: str, file_id: str, original_filename: str, detected_fields: list, deleted_fields: list) -> bool:
    now = datetime.now(timezone(timedelta(hours=9))).isoformat()

    log_payload = {
        "code": "200",
        "message": "파일 업로드 및 개인 정보 삭제를 성공했습니다",
        "data": {
            "deleted_at": now,
            "deleted_by": "AI_server",
            "user_id": user_id,
            "file_id": file_id,
            "detected_pii_fields": detected_fields,
            "deleted_fields": deleted_fields,
            "deletion_method": "anonymization",
            "deletion_reason": "policy_auto",
            "deletion_status": "success",
            "validation_result": "no remaining PII",
            "original_filename": original_filename
        }
    }

    query = """
        INSERT INTO pii_logs (
            user_id,
            file_id,
            log_json
        ) VALUES (%s, %s, %s)
    """

    params = (user_id, file_id, json.dumps(log_payload, ensure_ascii=False))

    return insert_one(query, params)