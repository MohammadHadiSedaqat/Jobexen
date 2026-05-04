from pydantic import BaseModel, EmailStr, Field, field_validator , model_validator
from typing import Optional, List
import re
from datetime import date
from enum import Enum

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_coplexity(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("رمز عبور باید حداقل یک حرف بزرگ داشته باشد")

        if not re.search(r"[0-9]", v):
            raise ValueError("رمز عبور حداقل باید یک عدد داشته باشد")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("رمز عبور باید حداقل یک کاراکتر خاص (@، #، $ و...) داشته باشد")

        return v


class UserResponse(UserBase):
    id :int
    bio : Optional[str] = None
    reputation_score: int = 0
    specialty_score: int = 0
    is_verified: bool = False


class UserLogin(BaseModel):
    identifier: str
    password: str


class ForgetPasswordRequest(BaseModel):
    identifier: str


class ResetPassword(BaseModel):
    identifier: str
    code: str = Field(..., min_length=6, max_length=6)
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_complexity(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("رمز عبور باید حداقل یک حرف بزرگ داشته باشد")

        if not re.search(r"[0-9]", v):
            raise ValueError("رمز عبور حداقل باید یک عدد داشته باشد")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("رمز عبور باید حداقل یک کاراکتر خاص (@، #، $ و...) داشته باشد")

        return v

    @model_validator(mode="after")
    # @classmethod
    def check_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("رمز عبور و تکرار آن با هم مطابقت ندارند!")
        return self



    class Config:
        from_attributes = True


class EmploymentType(str, Enum):
    FULL_TIME = "Full-time"
    FREELANCE = "Freelance"
    OPEN_SOURCE = "Open-source"
    PERSONAL_PROJECT = "Personal_Project"
    OTHER = "Other"


class SkillLevel(str, Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    expert = "Expert"


class ExperienceCreate(BaseModel):
    job_title: str = Field(..., min_length=3, max_length=100)
    company_name: Optional[str] = None
    employment_type:EmploymentType =EmploymentType.FULL_TIME
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class UserSkillCreate(BaseModel):
    skill_name: str = Field(..., min_length=3, max_length=100)
    level: SkillLevel = SkillLevel.beginner
    description: Optional[str] = None


class UserProfileResponse(UserResponse):
    specialty: Optional[str] = None
    resume_file_url: Optional[str] = None
    social_links: dict = {}
    experiences: List[ExperienceCreate] = []
    skills: List[UserSkillCreate] = []



