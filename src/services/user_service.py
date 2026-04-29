import jwt
from fastapi import HTTPException, status
import traceback
from src.repositories.user_repository import UserRepository
from src.services.auth import AuthService, pwd_context
from src.api.response_models.schemas.user import UserCreate
import random
from src.services.mail_service import GmailMailService


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.auth_service = AuthService()
        self.mail_service = GmailMailService()

    def register_user(self, user_data: UserCreate):
        try:
            # ۱. بررسی نام کاربری
            existing_user = self.user_repo.get_by_username(user_data.username)
            if existing_user:
                raise HTTPException(status_code=400, detail="این نام کاربری قبلا انتخاب شده است!")

            # ۲. بررسی ایمیل (اصلاح شد: از user_repo استفاده کردیم)
            existing_email = self.user_repo.get_by_email(user_data.email)
            if existing_email:
                raise HTTPException(status_code=400, detail="این ایمیل قبلا انتخاب شده است!")

            # ۳. هش کردن پسورد
            hashed_password = self.auth_service.get_password_hash(user_data.password)

            # ۴. آماده‌سازی دیتا برای ذخیره
            new_user_dict = user_data.model_dump()
            new_user_dict["password"] = hashed_password

            # ۵. ساخت کاربر در دیتابیس
            created_user = self.user_repo.create(new_user_dict)
            return created_user

        except Exception as e:
            print("❌ زینب ارور واقعی اینجاست:")
            traceback.print_exc()
            # اگر ارور از نوع HTTPException بود، همان را برگردان
            if isinstance(e, HTTPException):
                raise e
            # در غیر این صورت، ارور ۵۰۰ با جزئیات بده
            raise HTTPException(status_code=500, detail=str(e))


    def login_user(self, identifier, plain_password):
        try:
            existing_user = self.user_repo.get_by_username(identifier)
            if not existing_user:
                existing_user = self.user_repo.get_by_email(identifier)

            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="نام کاربری یا "
                           "ایمیل اشتباه است"
                )


            is_password_correct=pwd_context.verify(plain_password,existing_user['password'])
            if not is_password_correct:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="نام کاربری/ایمیل یا رمز عبور اشتباه است"
                )

            return existing_user

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,)


    def login_for_access_token(self , identifier , password):
        user = self.login_user(identifier, password)
        token_data = {"sub":str(user["id"])}
        access_token = self.auth_service.create_access_token(data=token_data)
        return {
            "access_token" : access_token,
            "token_type" : "bearer",
        }


    async def request_password_reset(self,identifier):

        existing_user = await self.user_repo.get_user_by_identifier(identifier)

        if not existing_user:
            return {"message": "اگر حساب کاربری معتبری داشته باشید، ایمیل حاوی لینک بازیابی برای شما ارسال شد."}

        try:

            recovery_code = str(random.randint(100000, 999999))

            await self.user_repo.store_recovery_code(existing_user["id"], recovery_code)

            await self.mail_service.send_recovery_code(
                email_to=existing_user["email"],
                username=existing_user["username"],
                code=recovery_code
            )
            return {"message": "کد بازیابی رمز عبور با موفقیت به ایمیل شما ارسال شد."}

        except Exception as e:
            print(f"Error in password reset: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="خطایی در سیستم رخ داده است. لطفاً بعداً تلاش کنید."
            )

    async def reset_password_with_code(self, identifier: str, code: str, new_password: str):
        recovery_entry = await self.user_repo.get_recovery_code_entry(identifier, code)

        if not recovery_entry:
            raise HTTPException(
                status_code=400,
                detail="کد وارد شده نامعتبر، منقضی شده یا قبلاً استفاده شده است."
            )

        hashed_password = self.auth_service.get_password_hash(new_password)

        try:
            await self.user_repo.update_password(
                user_id=recovery_entry["user_id"],
                hashed_password=hashed_password
            )

            return {"message": "رمز عبور شما با موفقیت تغییر کرد. اکنون می‌توانید وارد شوید."}

        except Exception as e:
            print(f"Error during final password reset: {e}")
            raise HTTPException(status_code=500, detail="خطا در به روزرسانی رمز عبور")





