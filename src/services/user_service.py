# from typing import List
#
# import jwt
# from fastapi import HTTPException, status
# import traceback
# from src.repositories.user_repository import UserRepository
# from src.services.auth import AuthService, pwd_context
# from src.api.response_models.schemas.user import UserCreate, ExperienceCreate, UserSkillCreate
# import random
# from src.services.mail_service import GmailMailService
#
#
#
# class UserService:
#     def __init__(self):
#         self.user_repo = UserRepository()
#         self.auth_service = AuthService()
#         self.mail_service = GmailMailService()
#
#     def register_user(self, user_data: UserCreate):
#         from src.services.auth import AuthService , pwd_context
#         try:
#
#             existing_user = self.user_repo.get_by_username(user_data.username)
#             if existing_user:
#                 raise HTTPException(status_code=400, detail="این نام کاربری قبلا انتخاب شده است!")
#
#             existing_email = self.user_repo.get_by_email(user_data.email)
#             if existing_email:
#                 raise HTTPException(status_code=400, detail="این ایمیل قبلا انتخاب شده است!")
#
#             hashed_password = self.auth_service.get_password_hash(user_data.password)
#
#
#             new_user_dict = user_data.model_dump()
#             new_user_dict["password"] = hashed_password
#
#
#             created_user = self.user_repo.create(new_user_dict)
#             return created_user
#
#         except Exception as e:
#             print("❌ زینب ارور واقعی اینجاست:")
#             traceback.print_exc()
#
#             if isinstance(e, HTTPException):
#                 raise e
#
#             raise HTTPException(status_code=500, detail=str(e))
#
#
#     def login_user(self, identifier, plain_password):
#         try:
#             existing_user = self.user_repo.get_by_username(identifier)
#             if not existing_user:
#                 existing_user = self.user_repo.get_by_email(identifier)
#
#             if not existing_user:
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED,
#                     detail="نام کاربری یا "
#                            "ایمیل اشتباه است"
#                 )
#
#
#             is_password_correct=pwd_context.verify(plain_password,existing_user['password'])
#             if not is_password_correct:
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED,
#                     detail="نام کاربری/ایمیل یا رمز عبور اشتباه است"
#                 )
#
#             return existing_user
#
#         except HTTPException as e:
#             raise e
#
#         except Exception as e:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,)
#
#
#     def login_for_access_token(self , identifier , password):
#         user = self.login_user(identifier, password)
#         token_data = {"sub":str(user["id"])}
#         access_token = self.auth_service.create_access_token(data=token_data)
#         return {
#             "access_token" : access_token,
#             "token_type" : "bearer",
#         }
#
#
#     async def request_password_reset(self,identifier):
#
#         existing_user = await self.user_repo.get_user_by_identifier(identifier)
#
#         if not existing_user:
#             return {"message": "اگر حساب کاربری معتبری داشته باشید، ایمیل حاوی لینک بازیابی برای شما ارسال شد."}
#
#         try:
#
#             recovery_code = str(random.randint(100000, 999999))
#
#             await self.user_repo.store_recovery_code(existing_user["id"], recovery_code)
#
#             await self.mail_service.send_recovery_code(
#                 email_to=existing_user["email"],
#                 username=existing_user["username"],
#                 code=recovery_code
#             )
#             return {"message": "کد بازیابی رمز عبور با موفقیت به ایمیل شما ارسال شد."}
#
#         except Exception as e:
#             print(f"Error in password reset: {e}")
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="خطایی در سیستم رخ داده است. لطفاً بعداً تلاش کنید."
#             )
#
#
#     async def reset_password_with_code(self, identifier: str, code: str, new_password: str):
#         recovery_entry = await self.user_repo.get_recovery_code_entry(identifier, code)
#
#         if not recovery_entry:
#             raise HTTPException(
#                 status_code=400,
#                 detail="کد وارد شده نامعتبر، منقضی شده یا قبلاً استفاده شده است."
#             )
#
#         hashed_password = self.auth_service.get_password_hash(new_password)
#
#         try:
#             await self.user_repo.update_password(
#                 user_id=recovery_entry["user_id"],
#                 hashed_password=hashed_password
#             )
#
#             return {"message": "رمز عبور شما با موفقیت تغییر کرد. اکنون می‌توانید وارد شوید."}
#
#         except Exception as e:
#             print(f"Error during final password reset: {e}")
#             raise HTTPException(status_code=500, detail="خطا در به روزرسانی رمز عبور")
#
#
#     async def add_experience(self,user_id: int, experience: List[ExperienceCreate]):
#         results=[]
#         for experience_item in experience:
#             exp_dict = experience_item.model_dump()
#             await self.user_repo.add_experience(user_id, exp_dict)
#             results.append(experience_item.job_title)
#         return {"status": "success" , "added_experiences": results}
#
#
#     async def add_skill(self,user_id: int, skills: List[UserSkillCreate]):
#         results =[]
#         for skill_item in skills:
#             skill_dict = skill_item.model_dump()
#             await self.user_repo.add_skill(user_id, skill_dict)
#             results.append(skill_item.skill_name)
#
#         return {"status": "success" , "added_skills": results}
#
#

from typing import List, Any
import jwt
from fastapi import HTTPException, status
import traceback
import random
from src.repositories.user_repository import UserRepository
from src.api.response_models.schemas.user import UserCreate, ExperienceCreate, UserSkillCreate
from src.services.mail_service import GmailMailService


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()
        # به دلیل Circular Import، AuthService را اینجا مقداردهی نمی‌کنیم
        self.mail_service = GmailMailService()

    def register_user(self, user_data: UserCreate):
        # ایمپورت محلی برای شکستن چرخه
        from src.services.auth import AuthService
        try:
            existing_user = self.user_repo.get_by_username(user_data.username)
            if existing_user:
                raise HTTPException(status_code=400, detail="این نام کاربری قبلا انتخاب شده است!")

            existing_email = self.user_repo.get_by_email(user_data.email)
            if existing_email:
                raise HTTPException(status_code=400, detail="این ایمیل قبلا انتخاب شده است!")

            # استفاده مستقیم از متد کلاس AuthService
            hashed_password = AuthService.get_password_hash(user_data.password)

            new_user_dict = user_data.model_dump()
            new_user_dict["password"] = hashed_password

            created_user = self.user_repo.create(new_user_dict)
            return created_user

        except Exception as e:
            print("❌ زینب ارور واقعی اینجاست:")
            traceback.print_exc()
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=str(e))

    def login_user(self, identifier, plain_password):
        from src.services.auth import AuthService  # ایمپورت محلی
        try:
            existing_user = self.user_repo.get_by_username(identifier)
            if not existing_user:
                existing_user = self.user_repo.get_by_email(identifier)

            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="نام کاربری یا ایمیل اشتباه است"
                )

            # چک کردن پسورد با استفاده از AuthService
            is_password_correct = AuthService.verify_password(plain_password, existing_user['password'])
            if not is_password_correct:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="رمز عبور اشتباه است"
                )

            return existing_user

        except HTTPException as e:
            raise e
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="خطا در ورود")

    # def login_for_access_token(self, identifier, password):
    #     from src.services.auth import AuthService  # ایمپورت محلی
    #
    #     user = self.login_user(identifier, password)
    #     token_data = {"sub": str(user["id"])}
    #
    #     # استفاده مستقیم از متد کلاس
    #     access_token = AuthService.create_access_token(data=token_data)
    #     return {
    #         "access_token": access_token,
    #         "token_type": "bearer",
    #     }
    def login_for_access_token(self, identifier, password):
        # ۱. ایمپورت رو همین‌جا داخل متد انجام بده
        from src.services.auth import AuthService

        user = self.login_user(identifier, password)
        token_data = {"sub": str(user["id"])}

        # ۲. اینجا بنویس AuthService (بدون self.)
        access_token = AuthService.create_access_token(data=token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    async def request_password_reset(self, identifier):
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
            raise HTTPException(status_code=500, detail="خطا در ارسال ایمیل")

    async def reset_password_with_code(self, identifier: str, code: str, new_password: str):
        from src.services.auth import AuthService  # ایمپورت محلی

        recovery_entry = await self.user_repo.get_recovery_code_entry(identifier, code)
        if not recovery_entry:
            raise HTTPException(status_code=400, detail="کد وارد شده نامعتبر است.")

        hashed_password = AuthService.get_password_hash(new_password)

        try:
            await self.user_repo.update_password(
                user_id=recovery_entry["user_id"],
                hashed_password=hashed_password
            )
            return {"message": "رمز عبور با موفقیت تغییر کرد."}
        except Exception as e:
            raise HTTPException(status_code=500, detail="خطا در آپدیت رمز عبور")

    async def add_experience(self, user_id: int, experience: List[ExperienceCreate]):
        results = []
        for experience_item in experience:
            exp_dict = experience_item.model_dump()
            await self.user_repo.add_experience(user_id, exp_dict)
            results.append(experience_item.job_title)
        return {"status": "success", "added_experiences": results}

    async def add_skill(self, user_id: int, skills: List[UserSkillCreate]):
        results = []
        for skill_item in skills:
            skill_dict = skill_item.model_dump()
            await self.user_repo.add_skill(user_id, skill_dict)
            results.append(skill_item.skill_name)
        return {"status": "success", "added_skills": results}

    async def get_user_profile(self, user_id: int):
        profile = await self.user_repo.get_full_profile(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="User not found")

        profile.pop('password', None)
        return profile