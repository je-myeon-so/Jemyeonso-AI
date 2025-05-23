import os
from dotenv import load_dotenv, find_dotenv
env_path = find_dotenv()
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")