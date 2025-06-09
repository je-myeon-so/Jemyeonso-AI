from config import URL
from urllib.parse import urlparse
from mysql.connector import pooling, Error

parsed = urlparse(URL)

mysql_config = {
    "host": parsed.hostname,
    "user": parsed.username,
    "password": parsed.password,
    "database": parsed.path[1:],
    "port": parsed.port,  # 문자열로 환경 변수 받았을 경우 변환
    "charset": 'utf8mb4',
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
