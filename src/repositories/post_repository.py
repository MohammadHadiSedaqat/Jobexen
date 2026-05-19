
import json
import psycopg2.extras
from dns.e164 import query
from sqlalchemy.dialects.mysql import insert

from src.connections.sync_postgres import get_db_connection
from typing import Optional, Dict, List


class PostRepository:
    def __init__(self):
        self.get_connection = get_db_connection

    def create(self, post_data: dict) -> Optional[Dict]:
        query = """
                INSERT INTO posts (user_id, title, content, post_type, image_url, extra_data, slug , is_published)
                VALUES (%s, %s, %s, %s, %s, %s, %s , %s) RETURNING *; 
                """

        conn = self.get_connection()
        if not conn:
            raise ConnectionError("اتصال به دیتابیس برقرار نشد.")


        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            extra_data_val = post_data.get('extra_data', {})
            extra_data_json = json.dumps(extra_data_val)


            params = (
                post_data.get('user_id'),
                post_data.get('title'),
                post_data.get('content'),
                post_data.get('post_type', 'post'),
                post_data.get('image_url'),
                extra_data_json,
                post_data.get('slug'),
                post_data.get('is_published' , True)
            )

            cursor.execute(query, params)
            new_post = cursor.fetchone()
            conn.commit()


            return dict(new_post) if new_post else None

        except Exception as e:
            conn.rollback()

            print(f"❌ DATABASE ERROR IN CREATE: {e}")
            return None

        finally:
            cursor.close()
            conn.close()

    def is_slug_exists(self, slug: str) -> bool:

        query = "SELECT EXISTS(SELECT 1 FROM posts WHERE slug = %s) as slug_exists;"

        conn = self.get_connection()
        if not conn:
            raise ConnectionError("اتصال به دیتابیس برقرار نشد.")

        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query, (slug,))
            result = cursor.fetchone()

            return result['slug_exists'] if result else False
        except Exception as e:
            print(f"❌ DATABASE ERROR IN SLUG CHECK: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_all_published_posts(self , limit:int =10, offset:int=0 , post_type:str=None , search : str = None , tag:str = None , user_id :int = None ) :
        query = """
            SELECT 
                p.*,
                u.full_name,u.avatar_url,u.specialty,
                u.reputation_score , u.specialty_score,u.is_verified
            FROM posts p 
            JOIN users u ON p.user_id = u.id
        """

        conditions = ["p.is_published=true"]
        params=[]

        if post_type:
            conditions.append("p.post_type=%s")
            params.append(post_type)

        if search:
            conditions.append("(p.title ILIKE %s OR p.content ILIKE %s)")
            search_param =f"%{search}%"
            params.extend([search_param , search_param])

        if tag:
            conditions.append("p.extra_data @>%s")
            tag_json = json.dumps({"tags": [tag.lower()]})
            params.append(tag_json)

        if user_id:
            conditions.append("p.user_id=%s")
            params.append(user_id)

        if conditions:
            query +=" WHERE " +" AND ".join(conditions)

        query += " ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        conn = self.get_connection()
        if not conn:
            return []
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()

            formatted_posts = []
            for r in results:
                post_data = dict(r)

                post_data['author'] ={
                    'full_name': post_data.pop('full_name'),
                    'avatar_url': post_data.pop('avatar_url'),
                    'specialty': post_data.pop('specialty'),
                    'reputation_score': post_data.pop('reputation_score'),
                    "specialty_score": post_data.pop('specialty_score'),
                    "is_verified": post_data.pop('is_verified')
                }
                formatted_posts.append(post_data)

            return formatted_posts
        except Exception as e:
            print(f"❌ DATABASE ERROR IN GET ALL: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_posts_counts(self, post_type: str = None, search: str = None , tag:str = None , user_id:int = None ) :
        query = "SELECT COUNT(p.id) as total FROM posts p JOIN users u ON p.user_id = u.id WHERE is_published = true"
        params = []
        if post_type:
            query += " AND post_type=%s"
            params.append(post_type)

        if search:
            query += " AND (p.title ILIKE %s OR p.content ILIKE %s)"
            search_param =f"%{search}%"
            params.extend([search_param , search_param])

        if tag:
            query += " AND p.extra_data @> %s"
            tag_json = json.dumps({"tags": [tag.lower()]})
            params.append(tag_json)

        if user_id:
            query += " AND p.user_id=%s"
            params.append(user_id)


        conn = self.get_connection()
        if not conn:
            return 0
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query , params)
            results = cursor.fetchone()
            return results['total'] if results else 0
        except Exception as e:
            print(f"ERROR IN GET COUNTS: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()

    def get_post_by_slug(self, slug: str):
        query = """
        SELECT p.*,
        u.full_name,u.avatar_url,u.specialty,
        u.reputation_score , u.specialty_score,u.is_verified
        FROM posts p 
        JOIN users u ON p.user_id = u.id
        WHERE p.slug = %s AND p.is_published = true;"""

        conn = self.get_connection()
        if not conn:
            raise ConnectionError("اتصال به دیتابیس برقرار نشد.")
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query, [slug])
            results = cursor.fetchone()
            if not results:
                return None

            post_data = dict(results)

            post_data['author'] ={
                'full_name': post_data.pop('full_name'),
                'avatar_url': post_data.pop('avatar_url'),
                'specialty': post_data.pop('specialty'),
                'reputation_score': post_data.pop('reputation_score'),
                "specialty_score": post_data.pop('specialty_score'),
                "is_verified": post_data.pop('is_verified')
                }
            return post_data

        except Exception as e:
            print(f"❌ DATABASE ERROR IN GET POST BY SLUG: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_my_posts(self , user_id: int , limit:int =10 , offset:int = 0 ,post_type:str =None):
        query ="SELECT * FROM posts WHERE user_id= %s"
        params = [user_id]
        if post_type:
            query += " AND post_type=%s"
            params.append(post_type)

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        conn = self.get_connection()
        if not conn:
            return []
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(r) for r in results]

        except Exception as e:
            print(f"❌ DATABASE ERROR IN GET MY POSTS: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_my_posts_count(self, user_id: int , post_type:str =None):
        query ="SELECT COUNT(id) as total FROM posts WHERE user_id= %s"
        params = [user_id]
        if post_type:
            query += " AND post_type=%s"
            params.append(post_type)

        conn = self.get_connection()
        if not conn:
            return 0
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query, params)
            results = cursor.fetchone()
            return results['total'] if results else 0

        except Exception as e:
            print(f"ERROR IN GET COUNTS: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()

    def get_post_by_id_and_user(self , post_id:int , user_id:int ):
        query = "SELECT * FROM posts WHERE id=%s AND user_id=%s"
        params =[post_id, user_id]
        conn = self.get_connection()
        if not conn:
            return None
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query, params)
            results = cursor.fetchone()

            if  results is  None:
                print("there is no post whith this id")
                return None
            post_data = dict(results)
            return post_data
        except Exception as e:
            print(f"ERROR IN GET POST BY ID: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self,post_id:int):
        query ="SELECT * FROM posts WHERE id=%s"
        params = [post_id]
        conn = self.get_connection()
        if not conn:
            return None
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query, params)
            results = cursor.fetchone()
            if results is None:
                print("there is no post whith this id")
                return None
            post_data = dict(results)
            return post_data
        except Exception as e:
            print(f"ERROR IN GET POST BY ID: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def update(self ,post_id , update_data:dict):
        if not update_data:
            return None
        set_clauses=[]
        params=[]

        for key, value in update_data.items():
            set_clauses.append(f"{key}=%s")
            if key == 'extra_data' and isinstance(value, dict):
                params.append(json.dumps(value))
            else:
                params.append(value)

        query=f"UPDATE posts SET {','.join(set_clauses)} WHERE id=%s RETURNING *;"

        params.append(post_id)

        conn = self.get_connection()
        if not conn:
            return None
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query, params)
            results = cursor.fetchone()
            conn.commit()
            return results
        except Exception as e:
            print(f"ERROR IN UPDATE {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def delete(self , post_id:int , user_id:int ):
        query="DELETE FROM posts WHERE id=%s AND user_id=%s"
        params=[post_id, user_id]
        conn = self.get_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount>0
        except Exception as e:
            print(f"ERROR IN DELETE {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def add_view_if_unique(self , post_id:int , user_id:Optional[int] , ip_address:str ) ->bool:
        insert_view_query="INSERT INTO post_views (post_id , user_id , ip_address) VALUES(%s ,%s ,%s) ON CONFLICT DO NOTHING;"
        insert_post_query="UPDATE posts SET view_count = view_count+1 WHERE id = %s"

        conn = self.get_connection()
        if not conn:
            return False
        cursor = conn.cursor()
        try:
            cursor.execute(insert_view_query, (post_id, user_id , ip_address))
            if cursor.rowcount > 0:
                cursor.execute(insert_post_query, [post_id])
                conn.commit()
                return True

            conn.commit()
            return False
        except Exception as e:
            conn.rollback()
            print(f"ERROR IN ADD VIEW {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def toggle_like(self, post_id: int, user_id: int) -> dict:
        delete_like_query = "DELETE FROM likes WHERE post_id = %s AND user_id = %s;"
        insert_like_query = "INSERT INTO likes (post_id, user_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;"

        decrease_counter_query = "UPDATE posts SET likes_count = likes_count - 1 WHERE id = %s RETURNING likes_count;"
        increase_counter_query = "UPDATE posts SET likes_count = likes_count + 1 WHERE id = %s RETURNING likes_count;"

        conn = self.get_connection()
        if not conn:
            return {"status": "error", "likes_count": 0}

        cursor = conn.cursor()
        try:
            cursor.execute(delete_like_query, (post_id, user_id))

            if cursor.rowcount > 0:
                cursor.execute(decrease_counter_query, [post_id])
                fetch_result = cursor.fetchone()
                new_likes_count = fetch_result['likes_count'] if fetch_result else 0

                conn.commit()
                return {"status": "unliked", "likes_count": new_likes_count}

            else:
                cursor.execute(insert_like_query, (post_id, user_id))
                cursor.execute(increase_counter_query, [post_id])

                fetch_result = cursor.fetchone()
                new_likes_count = fetch_result['likes_count'] if fetch_result else 0

                conn.commit()
                return {"status": "liked", "likes_count": new_likes_count}



        except Exception as e:
            conn.rollback()
            import traceback
            print("🔻🔻🔻 ارور واقعی و کامل دیتابیس اینجاست 🔻🔻🔻")
            traceback.print_exc()
            print(f"❌ DATABASE ERROR IN TOGGLE LIKE: {e}")
            print("🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺")
            return {"status": "error", "likes_count": 0}
        finally:
            cursor.close()
            conn.close()