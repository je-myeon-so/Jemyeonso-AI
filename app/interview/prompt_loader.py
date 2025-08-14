import os
from pathlib import Path
from typing import Dict, Optional
import boto3
from app.config import REGION, ACCESS_KEY, SECRET_KEY, S3_BUCKET

class PromptCache:
    def __init__(self):
        self._cache: Dict[str, str] = {}
    
    def get(self, key: str) -> Optional[str]:
        return self._cache.get(key)
    
    def set(self, key: str, value: str) -> None:
        self._cache[key] = value
    
    def clear(self) -> None:
        self._cache.clear()

_prompt_cache = PromptCache()

class PromptLoader:
    def __init__(self):
        self.s3_client = None
        self._initialize_s3()
    
    def _initialize_s3(self):
        try:
            if ACCESS_KEY and SECRET_KEY and REGION and S3_BUCKET:
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                    region_name=REGION
                )
        except Exception as e:
            print(f"Warning: S3 client initialization failed: {e}")
            self.s3_client = None
    
    def _load_from_local(self, filename: str) -> Optional[str]:
        try:
            base_dir = Path(__file__).resolve().parent.parent  # app/interview → app
            prompt_path = base_dir / "prompts" / filename
            if prompt_path.exists():
                return prompt_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Failed to load prompt from local: {e}")
        return None
    
    def _load_from_s3(self, filename: str) -> Optional[str]:
        """Load prompt from S3"""
        if not self.s3_client:
            return None
        
        try:
            response = self.s3_client.get_object(
                Bucket=S3_BUCKET,
                Key=f"prompts/{filename}"
            )
            return response['Body'].read().decode('utf-8')
        except Exception as e:
            print(f"Failed to load prompt from S3: {e}")
            return None
    
    def load_prompt(self, filename: str) -> str:
        cached_prompt = _prompt_cache.get(filename)
        if cached_prompt:
            return cached_prompt
        
        prompt_content = self._load_from_local(filename)
        
        if prompt_content is None:
            print(f"Local prompt not found, trying S3 for: {filename}")
            prompt_content = self._load_from_s3(filename)
        
        if prompt_content is None:
            raise FileNotFoundError(f"Prompt '{filename}' not found in local or S3")
        
        _prompt_cache.set(filename, prompt_content)
        
        return prompt_content
    
    def preload_all_prompts(self):
        prompt_files = ["analysis.txt", "follow_up.txt", "question.txt"] # Add more prompt filenames as needed
        
        for filename in prompt_files:
            try:
                self.load_prompt(filename)
                print(f"✅ Preloaded prompt: {filename}")
            except Exception as e:
                print(f"❌ Failed to preload prompt {filename}: {e}")
    
    def clear_cache(self):
        _prompt_cache.clear()

_prompt_loader = PromptLoader()

def load_prompt(filename: str) -> str:
    return _prompt_loader.load_prompt(filename)

def preload_prompts():
    _prompt_loader.preload_all_prompts()

def clear_prompt_cache():
    _prompt_loader.clear_cache()
