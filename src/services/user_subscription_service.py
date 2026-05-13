from fastapi import HTTPException, status
from src.repositories.user_subscription_repository import UserSubscriptionRepository
from typing import Optional, Dict , Any, List
from src.api.response_models.schemas.user_subscription import UserSubscriptionResponse



class UserSubscriptionService:
    def __init__(self):
        self.subuser_repo = UserSubscriptionRepository()

    def get_subscription_plan(self)  -> List[Dict]:
        try:
            subscription_plan = self.subuser_repo.show_all()
            if not subscription_plan:
                raise HTTPException(status_code=404, detail="There is no subscription plan ")

            return subscription_plan

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    def purchase_subscription_by_user(self, sub_name: str, payment_method : str, user_id : int) -> Dict:
        try:
            subscription_purchase = self.subuser_repo.subscription_purchase(sub_name, payment_method, user_id)
            if not subscription_purchase:
                raise HTTPException(status_code=404, detail="There is no subscription plan ")
            return subscription_purchase


        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


    def show_subscription_status(self, user_id: int) -> Dict:
        try:
            subscription_status = self.subuser_repo.subscription_status(user_id)
            if not subscription_status:
                raise HTTPException(status_code=404, detail="There is no subscription plan ")

            return subscription_status
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def show_payment_history(self, user_id: int) -> Dict:
        try:
            payment_history = self.subuser_repo.payment_history(user_id)
            if not payment_history:
                raise HTTPException(status_code=404, detail="There is no payment history ")
            return payment_history

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def cancel_subscription_by_user(self, user_id: int) -> Dict:
        try:
            cancel_subscription = self.subuser_repo.cancel_subscription(user_id)
            if not cancel_subscription:
                raise HTTPException(status_code=404, detail="There is no subscription plan ")
            return cancel_subscription

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
