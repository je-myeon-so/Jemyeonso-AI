from config import USER, HOST, PORT, PASSWORD, DATABASE, CHARSET
from mysql.connector import pooling, Error

mysql_config = {
    "host": HOST,
    "user": USER,
    "password": PASSWORD,
    "database": DATABASE,
    "port": int(PORT) if PORT else 3306,  # 문자열로 환경 변수 받았을 경우 변환
    "charset": CHARSET,
}

# 커넥션 풀 생성
try:
    pool = pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        pool_reset_session=True,
        **mysql_config
    )
except Error as e:
    print("❌ 커넥션 풀 생성 실패:", e)
    pool = None

def get_connection():
    if pool:
        return pool.get_connection()
    return None
