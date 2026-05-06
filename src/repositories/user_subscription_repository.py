from datetime import datetime, timedelta
from fastapi import HTTPException, status
from src.connections.sync_postgres import get_db_connection
from typing import Optional, Dict , Any, List
import psycopg2.extras
from enum import Enum, IntEnum
from src.api.response_models.schemas.user_subscription import BillingCycle


class TimeDelta(IntEnum):
    monthly = 30
    six_months = 180
    yearly = 365


class UserSubscriptionRepository:
    def  __init__(self):
        self.get_connection = get_db_connection

    def show_all(self) -> List[Dict]:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            query = """SELECT name, description, price, billing_cycle ,features FROM subscription_plans"""
            cursor.execute(query)

            items = cursor.fetchall()

            if items is None:
                raise HTTPException(status_code = 404, detail="There is no plan")

            return [dict(item) for item in items]

        except HTTPException as e:
            if conn: conn.rollback()
            raise e

        except Exception as e:
            if conn: conn.rollback()
            raise HTTPException(status_code=500, detail="Internal Server Error")

        finally:
            if conn:
                conn.close()
                cursor.close()

    def subscription_purchase(self, sub_name: str, payment_method : str, user_id : int) -> Dict:
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            purchase_query = """ 
                INSERT INTO user_subscriptions (
                    subscription_plan, plan_id, user_id, price, payment_method, end_date, status, last_payment_id
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                RETURNING *;
            """

            cursor.execute(
                "SELECT plan_id, price, billing_cycle FROM subscription_plans WHERE name = %s",
                (sub_name,)
            )

            plan_info = cursor.fetchone()

            if not plan_info:
                raise HTTPException(status_code=404, detail="Plan not found")

            plan_id, price, billing_cycle = plan_info['plan_id'], plan_info['price'], plan_info['billing_cycle']

            payment_query = """
                        INSERT INTO payments (user_id, plan_id, amount, payment_status, transaction_id)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING payment_id;
                    """

            import uuid
            fake_transaction_id = f"TRX-{uuid.uuid4().hex[:10].upper()}"
            cursor.execute(payment_query, (user_id, plan_id, price, 'success', fake_transaction_id))
            payment_id = cursor.fetchone()['payment_id']

            if billing_cycle == 'monthly':
                days = TimeDelta.monthly.value if hasattr(TimeDelta.monthly, 'value') else TimeDelta.monthly
            elif billing_cycle == 'yearly':
                days = TimeDelta.yearly.value if hasattr(TimeDelta.yearly, 'value') else TimeDelta.yearly
            elif billing_cycle == 'six_months':
                days = TimeDelta.six_months.value if hasattr(TimeDelta.six_months, 'value') else TimeDelta.six_months
            else:
                days = 30

            end_date = datetime.now() + timedelta(days=days)
            values = (sub_name, plan_id, user_id, price, payment_method, end_date, 'active', payment_id)

            cursor.execute(purchase_query, values)
            result = cursor.fetchone()
            conn.commit()

            return dict(result)

        except HTTPException as e:
            if conn: conn.rollback()
            raise e


        except Exception as e:
            if conn: conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))

        finally:
            if conn:
                conn.close()
                cursor.close()