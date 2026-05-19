from typing import List, Any
from fastapi import APIRouter, Depends, status, HTTPException
from src.api.response_models.schemas.user import UserCreate, UserResponse, UserLogin, ResetPassword, ExperienceCreate, \
    UserSkillCreate, UserProfileResponse, UserUpdate, ExperienceUpdate, ExperienceResponse, UserSkillUpdate
from src.services import user_service
from src.services.auth import AuthService
from src.services.user_service import UserService
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/settings", tags=["Settings"])

