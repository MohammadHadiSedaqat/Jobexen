from tabnanny import check
from typing import List, Any
import jwt
from fastapi import HTTPException, status
import traceback
import random
from src.repositories.user_repository import UserRepository
from src.api.response_models.schemas.user import UserCreate, ExperienceCreate, UserSkillCreate, UserUpdate, \
    ExperienceUpdate, UserSkillUpdate, UserEducationCreate, UserEducationUpdate
from src.services.mail_service import GmailMailService


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.mail_service = GmailMailService()

    def register_user(self, user_data: UserCreate):

        from src.services.auth import AuthService
        try:
            existing_user = self.user_repo.get_by_username(user_data.username)
            if existing_user:
                raise HTTPException(status_code=400, detail="این نام کاربری قبلا انتخاب شده است!")

            existing_email = self.user_repo.get_by_email(user_data.email)
            if existing_email:
                raise HTTPException(status_code=400, detail="این ایمیل قبلا انتخاب شده است!")


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
        from src.services.auth import AuthService
        try:
            existing_user = self.user_repo.get_by_username(identifier)
            if not existing_user:
                existing_user = self.user_repo.get_by_email(identifier)

            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="نام کاربری یا ایمیل اشتباه است"
                )

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

    def login_for_access_token(self, identifier, password):
        from src.services.auth import AuthService

        user = self.login_user(identifier, password)
        token_data = {"sub": str(user["id"])}

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
        profile_record = await self.user_repo.get_full_profile(user_id)

        if not profile_record:
            raise HTTPException(status_code=404, detail="User not found")

        profile = dict(profile_record)

        profile.pop('password', None)
        return profile

    async def update_user_profile(self,user_id: int , user_data: UserUpdate):
        update_dict = user_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="هیچ داده‌ای برای آپدیت ارسال نشده است.")

        if "username" in update_dict:
            existing_username = self.user_repo.get_by_username(update_dict["username"])
            if existing_username and existing_username.get('id') != user_id:
                raise HTTPException(status_code=400 , detail="این یوزرنیم توسط شخص دیگری ثبت شده است!")

        if "email" in update_dict:
            existing_email = self.user_repo.get_by_email(update_dict["email"])
            if existing_email and existing_email.get('id') != user_id:
                raise HTTPException(status_code=400 , detail="این ایمیل توسط شخص دیگری ثبت شده است!")

        await self.user_repo.update_user(user_id, update_dict)

        return await self.get_user_profile(user_id)

    async def update_user_experience(self,experience_id :int ,user_id: int, experience: ExperienceUpdate):

        update_dict = experience.model_dump(exclude_unset=True)

        if not update_dict:
            raise HTTPException(status_code=400 , detail="No Data Provided to update")

        updated_exp = await self.user_repo.update_experience(
            experience_id=experience_id,
            user_id=user_id,
            exp_data=update_dict
        )

        if not updated_exp:
            raise HTTPException(
                status_code=404,
                detail="Experience not found or you don't have permission to edit it"
            )
        return updated_exp

    async def update_user_skills(self, user_id: int, skill_id: int, skill_data: UserSkillUpdate):
        skill_dict = skill_data.model_dump(exclude_unset=True)

        db_result = await self.user_repo.edit_user_skill(user_id, skill_id, skill_dict)

        if not db_result:
            raise HTTPException(status_code=400, detail="User skill cannot be edited.")

        return db_result

    async def delete_profile(self , user_id: int):
        deleted_profile = await self.user_repo.delete_user_profile(user_id)
        if not deleted_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"status": "success", "message": "پروفایل و تمامی اطلاعات شما با موفقیت حذف شد."}

    async def delete_experience(self,user_id: int, experience_id:int):
        deleted_exp = await self.user_repo.delete_experience(user_id, experience_id)
        if not deleted_exp:
            raise HTTPException(status_code=404, detail="Experience not found")
        return {"message":"تجربه کاری شما با موفقیت حذف شد"}

    async def delete_skill(self,user_id: int, skill_id:int):
        deleted_skill = await self.user_repo.delete_user_skills(user_id, skill_id)
        if not deleted_skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        return {"message": "مهارت با موفقیت از پروفایل شما حذف شد."}

    async def add_education(self, user_id: int, user_data: List[UserEducationCreate]):
        results = []
        for edu_item in user_data:
            edu_dict = edu_item.model_dump()
            db_result = await self.user_repo.add_user_education(user_id, edu_dict)
            if db_result:
                results.append(db_result)

        if not results:
            raise HTTPException(status_code=400, detail="User education cannot be created")

        return results

    async def edit_education(self, user_id: int, education_id: int, user_data: List[UserEducationUpdate]):
        results = []
        for edu_item in user_data:
            edu_dict = edu_item.model_dump()
            db_result = await self.user_repo.edit_user_education(user_id ,education_id, edu_dict)
            if db_result:
                results.append(db_result)

        if not results:
            raise HTTPException(status_code=400, detail="User education cannot be edited.")

        return results

    async def get_education(self, user_id: int):
        try:
            edu_info = await self.user_repo.get_user_education(user_id)
            if not edu_info:
                raise HTTPException(status_code=404, detail="Education not found")

            return edu_info

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def search_education(self, user_id: int, search_query: str):
        try:
            edu_info = await self.user_repo.search_user_education(user_id, search_query)
            if not edu_info:
                raise HTTPException(status_code=404, detail="Education not found")

            return edu_info

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_user_education(self, user_id: int ,education_id: int):
        try:
            edu_info = await self.user_repo.delete_education(user_id ,education_id)
            if not edu_info:
                raise HTTPException(status_code=404, detail="Education not found")

            return edu_info

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_experience(self, user_id: int):
        try:
            exp_info = await self.user_repo.get_user_experience(user_id)
            if not exp_info:
                raise HTTPException(status_code=404, detail="Education not found")

            return exp_info

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def search_experience(self, user_id: int, search_query: str):
        try:
            exp_info = await self.user_repo.search_user_experience(user_id, search_query)
            if not exp_info:
                raise HTTPException(status_code=404, detail="Education not found")

            return exp_info

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_skills(self, user_id: int):
        try:
            skill_info = await self.user_repo.get_user_skill(user_id)
            if not skill_info:
                raise HTTPException(status_code=404, detail="Education not found")

            return skill_info

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def search_skill(self, user_id: int, search_query: str):
        try:
            skill_info = await self.user_repo.search_user_skill(user_id, search_query)
            if not skill_info:
                raise HTTPException(status_code=404, detail="Education not found")

            return skill_info

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))