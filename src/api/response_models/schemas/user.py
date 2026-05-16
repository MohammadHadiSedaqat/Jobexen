from pydantic import BaseModel, EmailStr, Field, field_validator , model_validator
from typing import Optional, List
import re
from datetime import date, datetime
from enum import Enum

class UserBase(BaseModel):
    username: str = Field(None, min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$", examples=["alphanumeric username"])
    email: EmailStr
    full_name: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=250)
    phone_number: Optional[str] = Field(None, min_length=11 , max_length=11)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

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


class UserResponse(UserBase):
    id :int
    bio : Optional[str] = None
    reputation_score: int = 0
    specialty_score: int = 0
    is_verified: bool = False
    phone_number: Optional[str] = None


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
    company_name: Optional[str] = Field(None, max_length=100)
    employment_type:EmploymentType =EmploymentType.FULL_TIME
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class ExperienceUpdate(BaseModel):
    job_title: Optional[str] = Field(None, min_length=3, max_length=100)
    company_name: Optional[str] = Field(None, max_length=100)
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class ExperienceResponse(BaseModel):
    id:int
    job_title: str
    company_name: Optional[str] = None
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserSkillCreate(BaseModel):
    skill_name: str = Field(..., min_length=3, max_length=100)
    level: SkillLevel = SkillLevel.beginner
    description: Optional[str] = None


class UserSkillUpdate(BaseModel):
    # skill_id:int
    skill_name: Optional[str] = Field(None, min_length=3, max_length=100)
    level: Optional[SkillLevel] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserSkillShow(BaseModel):
    skill_id:int
    skill_name: Optional[str] = Field(None, min_length=3, max_length=100)
    level: Optional[SkillLevel] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    specialty: Optional[str] = None
    resume_file_url: Optional[str] = None
    social_links: dict = {}
    experiences: List[ExperienceResponse] = []
    skills: List[UserSkillShow] = []


class UserMinInfo(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    specialty: Optional[str] = None
    reputation_score: int = 0
    specialty_score: int = 0
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str]= Field(None,min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$", description="alphanumeric username")
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    city: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=250)
    phone_number: Optional[str] = None
    social_links: dict = {}
    avatar_url: Optional[str] = None
    specialty: Optional[str] = None


class UserEducationCreate(BaseModel):
    institution: Optional[str] = Field(None, max_length=100)
    degree: Optional[str] = Field(None, max_length=100)
    education_level : Optional[str] = Field(None, max_length=100)
    field_of_study : Optional[str] = Field(None, max_length=100)
    start_year : Optional[int] = None
    graduation_year: Optional[int] = None
    grade: Optional[str] = None
    is_current: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=250)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)


class UserEducationResponse(BaseModel):
    id: int
    user_id: int
    institution: Optional[str] = Field(None, max_length=100)
    degree: Optional[str] = Field(None, max_length=100)
    education_level : Optional[str] = Field(None, max_length=100)
    field_of_study : Optional[str] = Field(None, max_length=100)
    start_year : Optional[int] = None
    graduation_year: Optional[int] = None
    grade: Optional[str] = None
    is_current: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=250)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserEducationUpdate(BaseModel):
    institution: Optional[str] = Field(None, max_length=100)
    degree: Optional[str] = Field(None, max_length=100)
    education_level : Optional[str] = Field(None, max_length=100)
    field_of_study : Optional[str] = Field(None, max_length=100)
    start_year : Optional[int] = None
    graduation_year: Optional[int] = None
    grade: Optional[str] = None
    is_current: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=250)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)

    class Config:
        from_attributes = True