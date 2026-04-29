# import os
# from dotenv import load_dotenv
# from pydantic_settings import BaseSettings, SettingsConfigDict
#
# load_dotenv()
#
#
# class Settings(BaseSettings):
#
#     DATABASE_URL: str = os.getenv("LOCAL_DATABASE_URL")
#
#     SECRET_KEY: str = os.getenv("SECRET_KEY")
#     ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
#     ACCESS_TOKEN_EXPIRE_MINUTES_FOR_PASSWORDS:int = 15
#     MAIL_USERNAME: str
#     MAIL_PASSWORD: str
#     MAIL_FROM: str
#     MAIL_PORT: int
#     MAIL_SERVER: str
#     MAIL_FROM_NAME: str
#
#     class Config:
#         case_sensitive = True
#         env_file = ".env"
#
#
# settings = Settings()

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # پایدانتیک خودش این‌ها را از .env پیدا می‌کند (به شرطی که نام‌ها یکی باشد)
    LOCAL_DATABASE_URL: str
    NEON_DATABASE_URL: str

    # اینجا می‌گوییم DATABASE_URL پیش‌فرض همان لوکال باشد
    DATABASE_URL: str = ""

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ACCESS_TOKEN_EXPIRE_MINUTES_FOR_PASSWORDS: int = 15

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str

    # تنظیمات جدید پایدانتیک (V2)
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # این خط باعث می‌شود اگر متغیر اضافه‌ای در .env بود، ارور ندهد
        case_sensitive=True
    )

    def __init__(self, **values):
        super().__init__(**values)
        # بعد از لود شدن، DATABASE_URL را مقداردهی می‌کنیم
        if not self.DATABASE_URL:
            self.DATABASE_URL = self.LOCAL_DATABASE_URL


settings = Settings()