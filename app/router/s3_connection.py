from fastapi import APIRouter, UploadFile, Form, File
from app.core.s3_utils import test_s3_connection, test_bucket_access, upload_file_to_s3
from config import S3_BUCKET

router = APIRouter(tags=["S3 버킷 연결"])
@router.get("/s3/test-connection")
async def s3_connection_test():
    is_connected = test_s3_connection()
    has_access = test_bucket_access(S3_BUCKET)

    if is_connected and has_access:
        return {"status": "success", "message": "S3 연결 및 버킷 접근 성공"}
    else:
        return {"status": "fail", "message": "S3 연결 또는 버킷 접근 실패"}


@router.post("/s3/upload")
async def upload_file_to_s3_api(
    file: UploadFile = File(...),
    s3_key: str = Form(...)
):
    file_bytes = await file.read()
    content_type = file.content_type  # 예: application/pdf, application/json

    success = upload_file_to_s3(
        file_bytes=file_bytes,
        object_key=s3_key,
        content_type=content_type
    )

    if success:
        return {"status": "success", "message": f"{s3_key} 업로드 완료"}
    else:
        return {"status": "fail", "message": "업로드 실패"}
