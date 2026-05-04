from typing import List, Any
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.util import await_only

from src.api.response_models.schemas.user import UserCreate, UserResponse, UserLogin, ResetPassword, ExperienceCreate, \
    UserSkillCreate, UserProfileResponse
from src.services.auth import AuthService
from src.services.user_service import UserService
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/users", tags=["Users"])


profile_router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.post("/register", response_model=UserResponse)
async def register_user(user_in: UserCreate, service: UserService = Depends(UserService)):
    try:
        return service.register_user(user_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/login")
# async def login(
#     login_data: UserLogin,
#     user_service: UserService = Depends(UserService)
# ):
#     result = user_service.login_for_access_token(
#         identifier=login_data.identifier,
#         password=login_data.password
#     )
#     return result

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_service = UserService()
    # Swagger فیلد identifier رو به عنوان username می‌فرسته
    result = user_service.login_for_access_token(
        identifier=form_data.username,
        password=form_data.password
    )
    return result

@router.post("/forget-password")
async def forget_password(
    identifier: str,
    user_service: UserService = Depends(UserService)
):

    return await user_service.request_password_reset(identifier)

@router.post("/reset-password-confirm")
async def reset_password_confirm(
    data: ResetPassword,
    user_service: UserService = Depends(UserService)
):

    return await user_service.reset_password_with_code(
        identifier=data.identifier,
        code=data.code,
        new_password=data.password
    )

@profile_router.post("/experiences", status_code=status.HTTP_201_CREATED)
async def add_user_experiences(
    experiences: List[ExperienceCreate],
    current_user: Any = Depends(AuthService.get_current_user),
    service: UserService = Depends()
):

    return await service.add_experience(current_user['id'], experiences)

@profile_router.post("/skills",status_code=status.HTTP_201_CREATED)
async def add_user_skills(
        skills: List[UserSkillCreate],
        current_user: Any = Depends(AuthService.get_current_user),
        service: UserService = Depends()
):

    return await service.add_skill(current_user['id'], skills)

@profile_router.get("/my/profile", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
async def get_user_profile(
        current_user: Any = Depends(AuthService.get_current_user),
        service: UserService = Depends(UserService)
):
    return await service.get_user_profile(current_user['id'])