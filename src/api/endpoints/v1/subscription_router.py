from typing import List, Any
from fastapi import APIRouter, Depends, status, HTTPException
from src.api.response_models.schemas.subscription import SubscriptionPlanResponse, SubscriptionPlan, SubscriptionPlan
from src.services.auth import AuthService
from src.services.subscription_service import SubscriptionService


router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.post("/plans", response_model=SubscriptionPlanResponse, status_code=status.HTTP_201_CREATED)
def create_subscription_plan(
        sub_data: SubscriptionPlan,
        sub_service: SubscriptionService = Depends(SubscriptionService)
):
        return sub_service.create_subscription(sub_data)

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_all_subscription_plans(
        sub_service: SubscriptionService = Depends(SubscriptionService)
):
        return sub_service.show_all_subscription()

@router.patch("/plans/{plan_name}", response_model=SubscriptionPlanResponse, status_code=status.HTTP_200_OK)
async def update_subscription_plan(
        old_name: str,
        sub_data: SubscriptionPlan,
        sub_service: SubscriptionService = Depends(SubscriptionService)
):
        return sub_service.edit_subscription(old_name, sub_data)

@router.delete("/plans", status_code=status.HTTP_200_OK)
async def delete_all_subscription_plans(
        sub_service: SubscriptionService = Depends(SubscriptionService)
):
        return sub_service.delete_all_subscription()

@router.delete("/plans/{plan_id}", status_code=status.HTTP_200_OK)
async def delete_subscription_plan(
    plan_id: int,
    sub_service: SubscriptionService = Depends(SubscriptionService)
):
    return sub_service.delete_subscription(plan_id)
