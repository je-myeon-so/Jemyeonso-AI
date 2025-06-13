from typing import Dict, List, Optional
from datetime import datetime, timedelta
import hashlib
import threading
import asyncio
from contextlib import asynccontextmanager


class QuestionCacheManager:
    """질문 중복 방지를 위한 메모리 기반 캐시 매니저"""
    
    def __init__(self, ttl_hours: int = 24, max_questions_per_key: int = 20):
        self._cache: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        self._ttl_hours = ttl_hours
        self._max_questions_per_key = max_questions_per_key
        self._cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_interval_hours = 3  # 3시간마다 자동 정리
    
    def _generate_cache_key(self, document_id: str, job_type: str, 
                           question_category: str, question_level: str) -> str:
        """캐시 키 생성 (MD5 해시 사용)"""
        key_string = f"{document_id}:{job_type}:{question_category}:{question_level}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_expired(self, cache_entry: Dict) -> bool:
        """캐시 엔트리 만료 여부 확인"""
        return datetime.now() > cache_entry['expires_at']
    
    def get_previous_questions(self, document_id: str, job_type: str,
                              question_category: str, question_level: str) -> List[str]:
        """이전에 생성된 질문들 조회"""
        with self._lock:
            cache_key = self._generate_cache_key(document_id, job_type, question_category, question_level)
            cache_entry = self._cache.get(cache_key)
            
            if not cache_entry or self._is_expired(cache_entry):
                if cache_entry:
                    del self._cache[cache_key]
                return []
            
            return cache_entry['questions'].copy()
    
    def add_question(self, document_id: str, job_type: str,
                     question_category: str, question_level: str, question: str) -> None:
        """새 질문을 캐시에 추가"""
        with self._lock:
            cache_key = self._generate_cache_key(document_id, job_type, question_category, question_level)
            
            # 새 캐시 엔트리 생성 또는 기존 엔트리 가져오기
            if cache_key not in self._cache:
                self._cache[cache_key] = {
                    'questions': [],
                    'expires_at': datetime.now() + timedelta(hours=self._ttl_hours),
                    'document_id': document_id
                }
            
            # 질문 추가
            self._cache[cache_key]['questions'].append(question)
            
            # 최대 질문 수 제한 (메모리 절약)
            if len(self._cache[cache_key]['questions']) > self._max_questions_per_key:
                self._cache[cache_key]['questions'] = self._cache[cache_key]['questions'][-self._max_questions_per_key:]
    
    def clear_cache_by_document(self, document_id: str) -> int:
        """특정 document_id의 모든 캐시 삭제"""
        with self._lock:
            keys_to_delete = [
                key for key, value in self._cache.items()
                if value.get('document_id') == document_id
            ]
            
            for key in keys_to_delete:
                del self._cache[key]
            
            return len(keys_to_delete)
    
    def cleanup_expired_entries(self) -> int:
        """만료된 캐시 엔트리들 정리"""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, value in self._cache.items()
                if now > value['expires_at']
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def get_cache_stats(self) -> Dict:
        """캐시 통계 정보 반환"""
        with self._lock:
            total_entries = len(self._cache)
            total_questions = sum(len(entry['questions']) for entry in self._cache.values())
            
            return {
                'total_cache_entries': total_entries,
                'total_cached_questions': total_questions,
                'ttl_hours': self._ttl_hours,
                'max_questions_per_key': self._max_questions_per_key,
                'cleanup_interval_hours': self._cleanup_interval_hours
            }
    
    async def _periodic_cleanup(self):
        """주기적 캐시 정리 백그라운드 태스크"""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval_hours * 3600)  # 시간을 초로 변환
                cleaned_count = self.cleanup_expired_entries()
                if cleaned_count > 0:
                    print(f"🧹 자동 캐시 정리: {cleaned_count}개 만료된 항목 삭제됨")
            except asyncio.CancelledError:
                print("캐시 정리 태스크 중단됨")
                break
            except Exception as e:
                print(f"캐시 정리 중 오류: {e}")
    
    async def start_background_cleanup(self):
        """백그라운드 캐시 정리 태스크 시작"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            print(f"캐시 자동 정리 태스크 시작 (주기: {self._cleanup_interval_hours}시간)")
    
    async def stop_background_cleanup(self):
        """백그라운드 캐시 정리 태스크 중단"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            print("🛑 캐시 자동 정리 태스크 중단됨")


# 전역 캐시 인스턴스 (싱글톤)
question_cache = QuestionCacheManager()


@asynccontextmanager
async def cache_lifespan(app):
    """FastAPI 앱 라이프사이클 매니저 - 캐시 자동 정리 태스크 관리"""
    # 시작 시
    await question_cache.start_background_cleanup()
    yield
    # 종료 시
    await question_cache.stop_background_cleanup() 