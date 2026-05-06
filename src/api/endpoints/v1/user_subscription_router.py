from typing import List, Any
from fastapi import APIRouter, Depends, status, HTTPException, Form
from src.api.response_models.schemas.user_subscription import UserSubscriptionResponse, UserSubscriptionPurchaseResponse
from src.services.user_subscription_service import UserSubscriptionService
from src.services.auth import AuthService


router = APIRouter(prefix="/user-subscriptions", tags=["User Subscription"])

@router.get("/plans", response_model=List[UserSubscriptionResponse], status_code=status.HTTP_200_OK)
def get_subscription_plan(
        user_sub_service: UserSubscriptionService = Depends(UserSubscriptionService),
        current_user: Any = Depends(AuthService.get_current_user),
):
    return user_sub_service.get_subscription_plan()

@router.post("/purchase", response_model=UserSubscriptionPurchaseResponse, status_code=status.HTTP_201_CREATED)
def subscription_purchase_by_user(
        user_sub_service: UserSubscriptionService = Depends(UserSubscriptionService),
        current_user: Any = Depends(AuthService.get_current_user),
        plan_name: str = Form(...,max_length=100),
        payment_method : str = Form(...,max_length=100),
):
    subscription = user_sub_service.purchase_subscription_by_user(plan_name, payment_method, current_user['id'])
    return subscription