from app.core.mysql_database import get_connection

def get_context(interview_id: int):
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT question_type, question_level, job_type 
            FROM interviews 
            WHERE id = %s
        """, (interview_id,))
        return cursor.fetchone()
    except Exception as e:
        print("❌ DB 조회 실패:", e)
        return None
    finally:
        cursor.close()
        conn.close()
        
def fetch_one(query: str, params: tuple = ()):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print("❌ Fetch 실패:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def insert_one(query: str, params: tuple = ()):
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        print("❌ Insert 실패:", e)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()