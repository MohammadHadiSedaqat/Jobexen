from http.client import HTTPException
from sqlalchemy.dialects.mysql import insert
from src.connections.sync_postgres import get_db_connection
from typing import Optional, Dict , Any
import psycopg2.extras
from typing import Union


class UserRepository:
    def  __init__(self):
        self.get_connection = get_db_connection

    def create(self, user_data: Dict) -> Dict:

        query = """
                INSERT INTO users (username, email, password, full_name, city, bio, phone_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *; 
                """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            params = (
                user_data["username"],
                user_data["email"],
                user_data["password"],
                user_data.get("full_name"),
                user_data.get("city"),
                user_data.get("bio"),
                user_data.get("phone_number")
            )

            cursor.execute(query, params)
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

    def increase_reputation(self, user_id, reward_score):
        query = "UPDATE users SET reputation_score = reputation_score +%s WHERE id = %s"

        conn = self.get_connection()
        if conn is None:
            raise ConnectionError
        cursor = conn.cursor()
        try:
            cursor.execute(query, (reward_score,user_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user reputation: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def decrease_reputation(self, user_id, reward_score):
        query = "UPDATE users SET reputation_score = reputation_score -%s WHERE id = %s"

        conn = self.get_connection()
        if conn is None:
            raise ConnectionError
        cursor = conn.cursor()
        try:
            cursor.execute(query, (reward_score,user_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user reputation: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def increase_specialty_score(self, user_id, specialty_score):
        query = "UPDATE users SET specialty_score = specialty_score +%s WHERE id = %s"
        conn = self.get_connection()
        if conn is None:
            raise ConnectionError
        cursor = conn.cursor()
        try:
            cursor.execute(query, (specialty_score,user_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user specialty: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def decrease_specialty_score(self, user_id, specialty_score):
        query = "UPDATE users SET specialty_score = specialty_score -%s WHERE id = %s"
        conn = self.get_connection()
        if conn is None:
            raise ConnectionError
        cursor = conn.cursor()
        try:
            cursor.execute(query, (specialty_score,user_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user specialty: {e}")
            conn.rollback()
            return False
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

    async def execute_query(self, query: str, params: Union[tuple, dict] = None):
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

    async def execute_query_fetchone(self , query: str, params: Union[tuple, dict] = None):
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

    async def add_experience(self, user_id: int  , exp_data: dict):
        query = """
                INSERT INTO user_experiences (user_id, company_name, job_title, employment_type, start_date, end_date, 
                                              description)
                VALUES (%(user_id)s, %(company_name)s, %(job_title)s, %(employment_type)s, %(start_date)s, %(end_date)s, 
                        %(description)s)
                """
        params = {**exp_data, "user_id": user_id}
        await self.execute_query(query, params)

    async def add_skill(self , user_id: int , skill_data: dict):
        query_skill = """
                      INSERT INTO skills (name)
                      VALUES (%(skill_name)s) ON CONFLICT (name) DO
                      UPDATE SET name = EXCLUDED.name
                          RETURNING id;
                      """
        skill_result = await self.execute_query_fetchone(query_skill, skill_data)
        skill_id = skill_result['id']

        query_link = """
                     INSERT INTO user_skills (user_id, skill_id, level, description)
                     VALUES (%(user_id)s, %(skill_id)s, %(level)s, %(description)s) ON CONFLICT (user_id, skill_id) 
            DO 
                     UPDATE SET
                         level = EXCLUDED.level, 
                         description = EXCLUDED.description; 
                     """

        params_link = {
            "user_id": user_id,
            "skill_id": skill_id,
            "level": skill_data.get('level' , 'Intermediate'),
            "description": skill_data.get('description')
        }

        await self.execute_query(query_link, params_link)

    async def execute_query_all(self, query: str, params: tuple = None):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query, params)
            return cursor.fetchall()  # لیست کامل رو برمی‌گردونه
        except Exception as e:
            print(f"❌ Error in execute_query_all: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    async def get_full_profile(self, user_id: int):
        user_query = "SELECT * FROM users WHERE id = %s"
        user_data = await self.execute_query_fetchone(user_query, (user_id,))

        if not user_data:
            return None

        user_dict = dict(user_data)

        exp_query = "SELECT * FROM user_experiences WHERE user_id = %s"
        user_dict['experiences'] = await self.execute_query_all(exp_query, (user_id,))

        skill_query = """
                      SELECT us.*, s.name as skill_name
                      FROM user_skills us
                               JOIN skills s ON us.skill_id = s.id
                      WHERE us.user_id = %s
                      """
        user_dict['skills'] = await self.execute_query_all(skill_query, (user_id,))

        return user_dict

    async def update_user(self, user_id: int, user_data: dict):
        if not user_data:
            return
        set_clauses =[]

        for key in user_data.keys():
            set_clauses.append(f"{key} = %({key})s")

        set_query = ",".join(set_clauses)

        query = f"UPDATE users SET {set_query} WHERE id = %(user_id)s RETURNING *"

        params =user_data.copy()
        params['user_id'] = user_id

        updated_user =await self.execute_query_fetchone(query, params)
        return updated_user

    async def update_experience(self, experience_id: int, user_id: int, exp_data: dict):
        if not exp_data:
            return
        set_clauses = []
        for key in exp_data.keys():
            set_clauses.append(f"{key} = %({key})s")

        set_query = ",".join(set_clauses)
        query = f"update user_experiences set {set_query} WHERE user_id = %(user_id)s AND id = %(experience_id)s RETURNING *"

        params = exp_data.copy()
        params['experience_id'] = experience_id
        params['user_id'] = user_id

        updated_experience = await self.execute_query_fetchone(query, params)
        return updated_experience

    async def update_user_skills(self, user_id: int,skill_id:int, skill_data: dict):
        if not skill_data:
            return None
        set_clauses = []
        for key in skill_data.keys():
            set_clauses.append(f"{key} = %({key})s")

        set_query = ",".join(set_clauses)

        query= f"update user_skills set {set_query} where user_id = %(user_id)s and skill_id =%(skill_id)s RETURNING *"

        params = skill_data.copy()
        params['user_id'] = user_id
        params['skill_id'] = skill_id

        updated_user_skills = await self.execute_query_fetchone(query, params)
        return updated_user_skills

    async def  get_or_create_skill_by_name(self, skill_name:str)->int:
        query = """
                INSERT INTO skills (name)
                VALUES (%s) ON CONFLICT (name) DO 
                UPDATE SET name = EXCLUDED.name 
                    RETURNING id; 
                """

        conn=self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cursor.execute(query, (skill_name,))
            result = cursor.fetchone()
            return result["id"]
        finally:
            cursor.close()
            conn.close()

    async def delete_user_profile(self, user_id: int):
        query = "DELETE FROM users WHERE id = %s RETURNING *"
        return await self.execute_query_fetchone(query, (user_id,))

    async def delete_experience(self, user_id: int, experience_id:int):
        query = "DELETE FROM user_experiences WHERE id = %s AND user_id = %s RETURNING id"
        return await self.execute_query_fetchone(query, (experience_id, user_id))

    async def delete_user_skills(self, user_id: int, skill_id:int):
        query = "delete from user_skills where user_id = %s AND skill_id = %s returning skill_id"
        return await self.execute_query_fetchone(query, (skill_id, user_id))


