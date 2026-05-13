from pydantic import BaseModel, EmailStr, Field, field_validator , model_validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, field_validator , model_validator, computed_field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import date, datetime, timedelta
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


class UserSubscriptionSituation(BaseModel):
    subscription_plan: str
    plan_id: int
    status: str
    started_at: datetime
    end_date: datetime

    @computed_field
    @property
    def remaining_days(self) -> int:
        now = datetime.now()
        if now > self.end_date:
            return 0
        diff = self.end_date - now
        return diff.days

    class Config:
        from_attributes = True


class PaymentHistory(BaseModel):
    payment_id: int
    amount: float
    payment_status: str
    transaction_id: str
    paid_at: datetime

    subscription_plan: str

    class Config:
        from_attributes = True
