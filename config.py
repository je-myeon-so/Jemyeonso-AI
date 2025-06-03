import os
from dotenv import load_dotenv, find_dotenv
env_path = find_dotenv()
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

URL = os.getenv("DB_URL")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")

REGION = os.getenv("AWS_REGION_STATIC")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")
if not MODEL_NAME:
    raise ValueError("MODEL_NAME not found in .env")