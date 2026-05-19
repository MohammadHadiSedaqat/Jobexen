from pydantic import BaseModel, EmailStr, Field, field_validator , model_validator, HttpUrl
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, field_validator , model_validator, computed_field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import date, datetime, timedelta
from enum import Enum

class UpdateProfile(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=250)
    specialty: Optional[str] = Field(None, max_length=100)
    social_links: Optional[Dict[str, str]] = Field(default={})

    class Config:
        from_attributes = True

class UpdateAccount(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, pattern=r"^09\d{9}$")

    class Config:
        from_attributes = True


class UpdateUserExperience(BaseModel):
    company_name: Optional[str] = Field(None, max_length=100)
    job_title: str = Field(..., max_length=100)
    employment_type: Optional[str] = Field("Full-time", max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

class UpdateUserEducation(BaseModel):
    institution: str = Field(..., max_length=150)
    degree: Optional[str] = Field(None, max_length=100)
    graduation_year: Optional[int] = Field(None, ge=1300, le=2100)

    class Config:
        from_attributes = True

class UpdateUserSkill(BaseModel):
    skill_id: int = Field(..., description="آیدی مهارتی که از جدول skills انتخاب شده")
    level: Optional[str] = Field("Intermediate", description="سطح مهارت (مثلا: Expert, Beginner)")

    class Config:
        from_attributes = True