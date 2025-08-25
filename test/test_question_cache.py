import pytest
from app.core.question_cache import QuestionCacheManager
from datetime import datetime, timedelta

@pytest.fixture
def cache_manager():
    """테스트를 위한 새로운 캐시 매니저 인스턴스를 생성"""
    return QuestionCacheManager(ttl_hours=1, max_questions_per_key=3)

def test_add_and_get_questions(cache_manager):
    """질문 추가 및 조회가 정상적으로 동작하는지 테스트"""
    doc_id = "doc1"
    job = "backend"
    cat = "tech"
    level = "hard"

    # 처음에는 비어있어야 함
    assert cache_manager.get_previous_questions(doc_id, job, cat, level) == []

    # 질문 추가
    cache_manager.add_question(doc_id, job, cat, level, "질문1")
    cache_manager.add_question(doc_id, job, cat, level, "질문2")

    # 조회 확인
    assert cache_manager.get_previous_questions(doc_id, job, cat, level) == ["질문1", "질문2"]

def test_cache_expiration(cache_manager):
    """캐시 만료 로직이 정상 동작하는지 테스트"""
    doc_id = "doc2"
    job = "frontend"
    cat = "cs"
    level = "easy"

    cache_manager.add_question(doc_id, job, cat, level, "만료될 질문")
    
    # 캐시 엔트리의 만료 시간을 과거로 조작
    cache_key = cache_manager._generate_cache_key(doc_id, job, cat, level)
    cache_manager._cache[cache_key]['expires_at'] = datetime.now() - timedelta(hours=2)

    # 만료 후 조회 시 빈 리스트가 반환되어야 함
    assert cache_manager.get_previous_questions(doc_id, job, cat, level) == []
    # 내부 캐시에서도 삭제되었는지 확인
    assert cache_key not in cache_manager._cache

def test_max_questions_limit(cache_manager):
    """최대 질문 개수 제한이 잘 동작하는지 테스트"""
    doc_id = "doc3"
    job = "ai"
    cat = "project"
    level = "normal"

    cache_manager.add_question(doc_id, job, cat, level, "질문1")
    cache_manager.add_question(doc_id, job, cat, level, "질문2")
    cache_manager.add_question(doc_id, job, cat, level, "질문3")
    cache_manager.add_question(doc_id, job, cat, level, "질문4") # 여기서 질문1이 밀려나야 함

    questions = cache_manager.get_previous_questions(doc_id, job, cat, level)
    assert len(questions) == 3
    assert questions == ["질문2", "질문3", "질문4"]

def test_clear_cache_by_document(cache_manager):
    """특정 문서 ID의 모든 캐시가 잘 삭제되는지 테스트"""
    doc_id = "doc4"
    cache_manager.add_question(doc_id, "job1", "cat1", "level1", "질문A")
    cache_manager.add_question(doc_id, "job2", "cat2", "level2", "질문B")
    
    # 다른 문서 ID의 캐시
    cache_manager.add_question("another_doc", "job1", "cat1", "level1", "질문C")
    
    deleted_count = cache_manager.clear_cache_by_document(doc_id)
    assert deleted_count == 2
    
    # doc4의 캐시들이 삭제되었는지 확인
    assert cache_manager.get_previous_questions(doc_id, "job1", "cat1", "level1") == []
    assert cache_manager.get_previous_questions(doc_id, "job2", "cat2", "level2") == []
    
    # 다른 문서의 캐시는 남아있는지 확인
    assert cache_manager.get_previous_questions("another_doc", "job1", "cat1", "level1") == ["질문C"]