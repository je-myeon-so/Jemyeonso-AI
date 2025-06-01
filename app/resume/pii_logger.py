import json
from datetime import datetime, timezone, timedelta
from app.core.s3_utils import upload_file_to_s3

def log_pii_deletion(user_id: str, file_id: str, original_filename: str, detected_fields: list, deleted_fields: list) -> bool:
    now = datetime.now(timezone(timedelta(hours=9))).isoformat()

    log_payload = {
        "code": "200",
        "message": "파일 업로드 및 개인 정보 삭제를 성공했습니다",
        "data": {
            "deleted_at": now,
            "deleted_by": "backend_server_01",
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

    json_bytes = json.dumps(log_payload, ensure_ascii=False).encode("utf-8")
    object_key = f"pii-logs/{file_id}.json"

    return upload_file_to_s3(
        file_bytes=json_bytes,
        object_key=object_key,
        content_type="application/json"
    )