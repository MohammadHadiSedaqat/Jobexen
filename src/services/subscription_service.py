from fastapi import HTTPException, status
from src.repositories.subscription_repository import SubscriptionRepository
from typing import Optional, Dict , Any, List
from src.api.response_models.schemas.subscription import SubscriptionPlan, SubscriptionPlanResponse



class SubscriptionService:
    def __init__(self):
        self.sub_repo = SubscriptionRepository()

    def create_subscription(self, sub_data: SubscriptionPlan) -> Dict:
       try:
           new_sub_data = sub_data.model_dump()
           subscription = self.sub_repo.create(new_sub_data)

           if not subscription:
               raise HTTPException(status_code=400, detail="Subscription cannot be created")

           return subscription

       except HTTPException as e:
           raise e

       except Exception as e:
           raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    def show_all_subscription(self) -> List[Dict]:
        try:
            subscription_plan = self.sub_repo.show_all()
            if not subscription_plan and subscription_plan != []:
                raise HTTPException(status_code=404, detail="Subscription plan cannot be found")

            return subscription_plan

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    def edit_subscription(self, old_name: str, sub_data: SubscriptionPlan) -> Dict:
        try:
            edit_sub_data = sub_data.model_dump()
            edit_sub_data["old_name"] = old_name
            new_subscription_plan = self.sub_repo.edit(edit_sub_data)

            if not new_subscription_plan:
                raise HTTPException(status_code=400, detail="Subscription plan cannot be updated")

            return new_subscription_plan

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    def delete_all_subscription(self) -> Dict:
        try:
            subscription_plan = self.sub_repo.delete_all()
            if not subscription_plan:
                raise HTTPException(status_code=404, detail="Subscription plan cannot be found")

            return subscription_plan

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    def delete_subscription(self, plan_id: int) -> Dict:
        try:
            subscription_plan = self.sub_repo.delete_one(plan_id)
            if not subscription_plan:
                raise HTTPException(status_code=404, detail="Subscription plan cannot be found")

            return subscription_plan

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
