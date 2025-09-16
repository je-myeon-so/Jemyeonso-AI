from fastapi import APIRouter
from app.core.question_cache import question_cache

router = APIRouter(tags=["캐시 관리"])


@router.delete("/questions/cache/{document_id}")
def clear_question_cache(document_id: str):
    """특정 이력서의 질문 캐시 삭제"""
    try:
        deleted_count = question_cache.clear_cache_by_document(document_id)
        return {
            "code": 200,
            "message": f"문서 {document_id}의 질문 캐시 {deleted_count}개 항목이 삭제되었습니다.",
            "data": {"deleted_entries": deleted_count}
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"캐시 삭제 중 오류 발생: {str(e)}"
        }


@router.post("/questions/cache/cleanup")
def cleanup_expired_cache():
    """만료된 캐시 정리"""
    try:
        cleaned_count = question_cache.cleanup_expired_entries()
        return {
            "code": 200,
            "message": f"만료된 캐시 {cleaned_count}개 항목이 정리되었습니다.",
            "data": {"cleaned_entries": cleaned_count}
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"캐시 정리 중 오류 발생: {str(e)}"
        }


@router.get("/questions/cache/stats")
def get_cache_stats():
    """캐시 통계 정보 조회"""
    try:
        stats = question_cache.get_cache_stats()
        return {
            "code": 200,
            "message": "캐시 통계 정보를 조회했습니다.",
            "data": stats
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"캐시 통계 조회 중 오류 발생: {str(e)}"
        }
