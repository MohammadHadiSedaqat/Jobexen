from fastapi import HTTPException
from src.connections.sync_postgres import get_db_connection
from typing import Optional, Dict , Any, List
import psycopg2.extras
import json

class SubscriptionRepository:
    def __init__(self):
        self.get_connection = get_db_connection

    def create(self, sub_data: Dict) -> Dict:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            get_info = """
                    SELECT 1 FROM subscription_plans WHERE name = %s LIMIT 1;
                    """

            cursor.execute(get_info, (sub_data["name"],))
            if cursor.fetchone() is not None:
                raise HTTPException(status_code=400, detail=f"Subscription {sub_data["name"]} exists")

            query = """
                   INSERT INTO subscription_plans (name, description, price, billing_cycle, features, status)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;
                   """

            params = (
                sub_data["name"],
                sub_data.get("description"),
                sub_data["price"],
                sub_data["billing_cycle"],
                json.dumps(sub_data.get("features", {})),
                sub_data.get("status", "active"),
            )

            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.commit()
            return result

        except HTTPException as e:
            if conn: conn.rollback()
            raise e

        except Exception as e:
            if conn: conn.rollback()
            print(f"❌ Error in SubRepository.create: {e}")
            raise e

        finally:
            if conn:
                cursor.close()
                conn.close()

    def show_all(self) -> List[Dict]:
        conn = None
        try:
           conn = self.get_connection()
           cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
           query = """ SELECT * FROM subscription_plans """

           cursor.execute(query)
           return cursor.fetchall()

        except HTTPException as e:
            if conn: conn.rollback()
            raise e

        except Exception as e:
           if conn: conn.rollback()
           print(f"❌ Error in SubRepository.show_all {e}")
           raise e

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def edit(self, sub_data: Dict) -> Dict:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            get_info = """
                SELECT 1 FROM subscription_plans WHERE name = %s LIMIT 1;
            """

            cursor.execute(get_info, (sub_data["old_name"],))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Subscription does not exist")

            query = """
                UPDATE subscription_plans 
                SET name = %s, description = %s, price = %s, billing_cycle = %s, features = %s, status = %s
                WHERE name = %s 
                RETURNING *;
            """

            params = (
                sub_data["name"],
                sub_data.get("description"),
                sub_data["price"],
                sub_data["billing_cycle"],
                json.dumps(sub_data.get("features", {})),
                sub_data.get("status", "active"),
                sub_data["old_name"],
            )

            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.commit()
            return result

        except HTTPException as e:
            if conn: conn.rollback()
            raise e

        except Exception as e:
            if conn: conn.rollback()
            print(f"❌ Error in SubRepository.: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

        finally:
            if conn:
                cursor.close()
                conn.close()

    def delete_all(self) -> Dict:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = """
                TRUNCATE TABLE subscription_plans RESTART IDENTITY CASCADE;
            """

            cursor.execute("SELECT 1 FROM subscription_plans LIMIT 1;")
            if cursor.fetchone() is None:
                return {"message": "There is no subscription plan to delete"}

            cursor.execute(query)
            conn.commit()


            return {"message": "All subscription plans deleted"}
        except HTTPException as e:
            if conn: conn.rollback()
            raise e

        except Exception as e:
            if conn: conn.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")

        finally:
            if conn:
                 cursor.close()
                 conn.close()

    def delete_one(self, plan_id: int) -> Dict:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = """
                DELETE FROM subscription_plans WHERE plan_id = %s RETURNING *;
            """

            cursor.execute(query, (plan_id,))
            delete_plan = cursor.fetchone()

            if delete_plan is None:
                raise HTTPException(status_code=400, detail=f"Plan with id {plan_id} not found")


            conn.commit()
            return {"message": "subscription plan deleted"}

        except HTTPException as e:
            if conn: conn.rollback()
            raise e

        except Exception as e:
            if conn: conn.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")

        finally:
            if conn:
                cursor.close()
                conn.close()