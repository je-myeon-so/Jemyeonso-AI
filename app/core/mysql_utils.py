from app.core.mysql_database import get_connection

def update_redacted_resume_content(document_id: int, redacted_text: str) -> bool:
    """
    기존 documents 테이블에서 content를 redacted_text로 업데이트합니다.

    Args:
        document_id (int): 수정 대상 문서 ID
        redacted_text (str): PII 제거된 본문 텍스트

    Returns:
        bool: 성공 여부
    """
    query = """
        UPDATE documents
        SET content = %s, updated_at = NOW()
        WHERE id = %s AND type = 'resume'
    """
    params = (redacted_text, document_id)

    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        print("❌ content 업데이트 실패:", e)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()