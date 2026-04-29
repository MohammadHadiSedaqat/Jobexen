from fastapi import APIRouter, Depends, status, HTTPException
from src.api.response_models.schemas.user import UserCreate, UserResponse , UserLogin ,ResetPassword
from src.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse)
async def register_user(user_in: UserCreate, service: UserService = Depends(UserService)):
    try:
        return service.register_user(user_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(
    login_data: UserLogin,
    user_service: UserService = Depends(UserService)
):
    result = user_service.login_for_access_token(
        identifier=login_data.identifier,
        password=login_data.password
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

# {
#   "username": "Hadi1234",
#   "email": "hadisedaghat1384@gmail.com",
#   "full_name": "mohammadhadisedaghat",
#   "city": "Qom",
#   "bio": "string",
#   "password": "Hadi*1234"
# }