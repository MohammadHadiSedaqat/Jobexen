from csv import DictWriter
from typing import List, Any, Dict
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.util import await_only

from src.api.response_models.schemas.user import UserCreate, UserResponse, UserLogin, ResetPassword, ExperienceCreate, \
    UserSkillCreate, UserProfileResponse, UserUpdate, ExperienceUpdate, ExperienceResponse, UserSkillUpdate, \
    UserEducationResponse, UserEducationCreate, UserEducationUpdate
from src.services import user_service
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


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_service = UserService()

    result = user_service.login_for_access_token(
        identifier=form_data.username,
        password=form_data.password
    )
    return result

@router.post("/forget_password")
async def forget_password(
    identifier: str,
    user_service: UserService = Depends(UserService)
):

    return await user_service.request_password_reset(identifier)

@router.post("/reset_password_confirm")
async def reset_password_confirm(
    data: ResetPassword,
    user_service: UserService = Depends(UserService)
):

    return await user_service.reset_password_with_code(
        identifier=data.identifier,
        code=data.code,
        new_password=data.password
    )


@profile_router.get("/me/profile", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
async def get_user_profile(
        current_user: Any = Depends(AuthService.get_current_user),
        service: UserService = Depends(UserService)
):
    return await service.get_user_profile(current_user['id'])


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


@profile_router.patch("/me/experiences/{experience_id}", response_model=ExperienceResponse,status_code=status.HTTP_200_OK)
async def update_experience(
        experience_id: int,
        experience_data: ExperienceUpdate,
        current_user: Any = Depends(AuthService.get_current_user),
        service: UserService = Depends()
):

    update_exp = await service.update_user_experience(
        experience_id=experience_id,
        user_id=current_user['id'],
        experience=experience_data
    )
    return update_exp


@profile_router.patch("/me/skills/{skill_id}" , status_code=status.HTTP_200_OK)
async def update_user_skills(
    skill_id: int,
    skill_data: UserSkillUpdate,
    current_user: Any = Depends(AuthService.get_current_user),
    service: UserService = Depends()
):
    update_exp = await service.update_user_skills(
        user_id=current_user['id'],
        old_skill_id=skill_id,
        skill_data=skill_data
    )
    return update_exp


@profile_router.patch("/me/profile", response_model=UserProfileResponse ,status_code=status.HTTP_200_OK)
async def update_profile(
        user_data:UserUpdate,
        current_user: Any = Depends(AuthService.get_current_user),
        service: UserService = Depends()
):
    user_id = current_user['id']
    result = await service.update_user_profile(user_id, user_data)
    return result


@profile_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile(
        current_user: Any = Depends(AuthService.get_current_user),
        service: UserService = Depends()
):
    await service.user_repo.delete_user_profile(user_id=current_user['id'])
    return None


@profile_router.delete("/me/experiences/{exp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_experience(
        exp_id: int,
        current_user: Any = Depends(AuthService.get_current_user),
        service: UserService = Depends()
):
    return await service.delete_experience(current_user['id'], exp_id)


@profile_router.delete("/me/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_skill(
        skill_id: int,
        current_user: Any = Depends(AuthService.get_current_user),
        service: UserService = Depends()
):
    return await service.delete_skill(current_user['id'], skill_id)


@profile_router.get("/me/education", response_model=List[UserEducationResponse], status_code=status.HTTP_200_OK)
async def get_user_education(
        current_user: Any = Depends(AuthService.get_current_user),
        service: UserService = Depends()
):
    return await service.get_education(current_user['id'])

@profile_router.post("/me/education", response_model=List[UserEducationResponse], status_code=status.HTTP_201_CREATED)
async def create_user_education(
        education_data: List[UserEducationCreate],
        current_user: Any = Depends(AuthService.get_current_user),
        service: UserService = Depends()
):
    return await service.add_education(current_user['id'], education_data)


@profile_router.patch("/me/education/{education_id}", response_model=List[UserEducationResponse], status_code=status.HTTP_200_OK)
async def update_user_education(
        education_data: List[UserEducationUpdate],
        education_id: int,
        current_user: Any = Depends(AuthService.get_current_user),
        service: UserService = Depends()
):
    return await service.edit_education(current_user['id'], education_id, education_data)

@profile_router.delete("/me/education/{education_id}", status_code=status.HTTP_200_OK)
async def delete_user_education(
        education_id: int,
        current_user: Any = Depends(AuthService.get_current_user),
        service: UserService = Depends()
):
    return await service.delete_user_education(current_user['id'], education_id)
