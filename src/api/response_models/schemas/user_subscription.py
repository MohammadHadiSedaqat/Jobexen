from pydantic import BaseModel, EmailStr, Field, field_validator , model_validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import date, datetime
from enum import Enum


class BillingCycle(str, Enum):
    monthly = 'monthly'
    six_months = 'six_months'
    yearly = 'yearly'



class UserSubscriptionResponse(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    billing_cycle: BillingCycle
    features: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True



class PaymentMethodEnum(str, Enum):
    online = "online"
    card_to_card = "card_to_card"
    wallet = "wallet"


class UserSubscriptionPurchaseRequest(BaseModel):
    plan_name: str
    payment_method: PaymentMethodEnum = PaymentMethodEnum.online


class UserSubscriptionPurchaseResponse(BaseModel):
    subscription_plan: str
    user_id: int
    price: Decimal
    payment_method: str
    started_at: datetime
    end_date: datetime
    status:str = 'active'

    class Config:
        from_attributes = True
