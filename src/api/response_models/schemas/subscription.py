from pydantic import BaseModel, EmailStr, Field, field_validator , model_validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import date, datetime
from enum import Enum


class BillingCycle(str, Enum):
    monthly = 'monthly'
    six_months = '6_months'
    yearly = 'yearly'


class SubscriptionPlan(BaseModel):
    name: str = Field(...,min_length=3, max_length=50, example="")
    description: Optional[str] = Field(None, max_length=100, example="")
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    billing_cycle: BillingCycle
    features: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: str = Field(default="active", pattern="^(active|inactive|archived)$")

    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("price must be greater than or equal to zero")
        return v

    @field_validator('features')
    @classmethod
    def validate_features(cls, v: Optional[Dict]):
        if v is not None and len(v) == 0:
            pass
        return v

    class Config:
        from_attributes = True
        json_response = {
            "example": {
                "name": "پلن طلایی",
                "description": "دسترسی نامحدود به تمام منابع",
                "price": 99.99,
                "billing_cycle": "monthly",
                "features": {"storage": "100GB", "support": "24/7"},
                "status": "active"
            }
        }


class SubscriptionPlanResponse(SubscriptionPlan):
    plan_id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    billing_cycle: BillingCycle
    features: Optional[Dict[str, Any]] = None
    status: str = "active"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

