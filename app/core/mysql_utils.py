from app.core.mysql_database import get_connection
        
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