import os
from dotenv import load_dotenv, find_dotenv
env_path = find_dotenv()
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

# 데이터베이스 연결 설정
HOST = os.getenv("DB_HOST")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
PORT = os.getenv("DB_PORT", 3306)  # 기본값 3306
DATABASE = os.getenv("DB_NAME")
CHARSET = os.getenv("DB_CHARSET", "utf8mb4")  # 기본값 utf8mb4

# AWS S3 연결 설정
REGION = os.getenv("AWS_REGION_STATIC")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")

# 필수 환경 변수 검증
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")
if not MODEL_NAME:
    raise ValueError("MODEL_NAME not found in .env")