from http.client import HTTPException
from sqlalchemy.dialects.mysql import insert
from src.connections.sync_postgres import get_db_connection
from typing import Optional, Dict
import psycopg2.extras

class UserRepository:
    def  __init__(self):
        self.get_connection = get_db_connection

    def create(self, user_data: Dict) -> Dict:

        query = """
            INSERT INTO users (username, email, password, full_name, city)
            VALUES (%(username)s, %(email)s, %(password)s, %(full_name)s, %(city)s)
            RETURNING id, username, email, reputation_score, specialty_score, is_verified;
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, user_data)
            return cursor.fetchone()
        except Exception as e:
            print(f"❌ Error in UserRepository.create: {e}")
            raise e
        finally:
            cursor.close()
            conn.close()

    def get_by_username(self, username: str) -> Optional[Dict]:

        query = "SELECT * FROM users WHERE username = %s"
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (username,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_by_email(self, email: str) -> Optional[Dict]:

        query = "SELECT * FROM users WHERE email = %s"
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (email,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def get_by_phone_number(self, phone_number: str) -> Optional[Dict]:
        query = "SELECT id, phone_number FROM users WHERE phone_number = %s"
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (phone_number,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, user_id: int) -> Optional[Dict]:
        query = "SELECT * FROM users WHERE id = %s"
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    async def get_user_by_identifier(self , identifier: str) -> Optional[Dict]:
        query = "SELECT * FROM users WHERE username = %s OR email = %s"
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (identifier,identifier))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    async def store_recovery_code(self,user_id:int , code:str):
        delete_query = "DELETE FROM users WHERE id = %s"
        insert_query = "INSERT INTO password_recovery (user_id, code) VALUES (%s, %s)"
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(delete_query, (code,))
            cursor.execute(insert_query, (user_id,code))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error storing recovery code: {e}")
            raise e
        finally:
            cursor.close()
            conn.close()

    async def execute_query(self, query: str, params: tuple = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"❌ خطا در اجرای کوئری: {e}")
            raise e
        finally:
            cursor.close()
            conn.close()

    async def execute_query_fetchone(self , query: str, params: tuple = None):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    async def get_recovery_code_entry(self,identifier: str ,code: str):
        query = """
                SELECT pr.*, u.id as user_id
                FROM password_recovery pr
                         JOIN users u ON pr.user_id = u.id
                WHERE (u.email = %s OR u.username = %s)
                  AND pr.code = %s
                  AND pr.is_used = FALSE
                  AND pr.expires_at > NOW(); 
                """
        params = (
            identifier,
            identifier,
            code,
        )
        return await self.execute_query_fetchone(query, params)

    async def update_password(self , user_id , hashed_password):
        update_user_query = "UPDATE users SET password = %s WHERE id = %s"
        await self.execute_query(update_user_query, (hashed_password, user_id))

        mark_used_query = "UPDATE password_recovery SET is_used = TRUE WHERE user_id = %s"
        await self.execute_query(mark_used_query, (user_id,))

