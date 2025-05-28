import os
from dotenv import load_dotenv, find_dotenv
env_path = find_dotenv()
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
USER = os.getenv("DB_USER")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
PASSWORD = os.getenv("DB_PASSWORD")
DATABASE = os.getenv("DB_NAME")
CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")
if not MODEL_NAME:
    raise ValueError("MODEL_NAME not found in .env")