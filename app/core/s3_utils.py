import mimetypes
import boto3
from config import REGION, ACCESS_KEY, SECRET_KEY, S3_BUCKET

s3 = boto3.client(
    "s3",
    aws_access_key_id= ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

def upload_file_to_s3(file_bytes: bytes, object_key: str, content_type: str = None) -> bool:
    """
    S3 버킷에 파일 업로드 (PDF, JSON 등 제한 없음)

    :param file_bytes: 업로드할 파일의 내용 (bytes)
    :param object_key: S3 내 저장 경로 (예: 'logs/resume.json', 'uploads/resume.pdf')
    :param content_type: MIME 타입 (예: 'application/json', 'application/pdf') — 생략 시 자동 추정
    :return: 업로드 성공 여부
    """
    if content_type is None:
        content_type, _ = mimetypes.guess_type(object_key)
        if content_type is None:
            content_type = "application/octet-stream"  # fallback

    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=object_key,
            Body=file_bytes,
            ContentType=content_type
        )
        print(f"✅ S3 업로드 성공: s3://{S3_BUCKET}/{object_key}")
        return True
    except Exception as e:
        print(f"❌ S3 업로드 실패: {e}")
        return False

def test_s3_connection() -> bool:
    try:
        s3.list_buckets()
        return True
    except Exception as e:
        print("❌ S3 연결 실패:", e)
        return False

def test_bucket_access(bucket_name: str) -> bool:
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except Exception as e:
        print(f"❌ 버킷 접근 실패 ({bucket_name}):", e)
        return False