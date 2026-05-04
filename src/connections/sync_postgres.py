
import psycopg2
from psycopg2.extras import RealDictCursor
from src.config import settings

def get_db_connection():

    try:
        conn = psycopg2.connect(
            dsn=settings.DATABASE_URL,
            cursor_factory=RealDictCursor
        )

        conn.autocommit = True
        return conn
    except Exception as e:

        print(f"❌ خطای اتصال به دیتابیس: {e}")
        return None