from abc import ABC, abstractmethod
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType, NameEmail
from src.config import settings

class BaseMailService(ABC):
    @abstractmethod
    async def send_recovery_code(self,email_to:str,username: str, code :str):
        pass

class GmailMailService(BaseMailService):
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME = settings.MAIL_USERNAME,
            MAIL_PASSWORD = settings.MAIL_PASSWORD,
            MAIL_FROM = settings.MAIL_FROM,
            MAIL_PORT = settings.MAIL_PORT,
            MAIL_SERVER = settings.MAIL_SERVER,
            MAIL_FROM_NAME = settings.MAIL_FROM_NAME,
            MAIL_STARTTLS = True,
            MAIL_SSL_TLS = False,
            USE_CREDENTIALS = True
        )

    async def send_recovery_code(self, email_to: str, username: str, code: str):
        message = MessageSchema(
            subject="بازیابی حساب کاربری Jobexen",
            # recipients=[NameEmail(email=email_to)],
            recipients=[NameEmail(name=username, email=email_to)],
            body=f"سلام {username} عزیز،\nنام کاربری شما: {username}\nکد تایید بازیابی رمز عبور: {code}",
            subtype=MessageType.plain
        )
        fm = FastMail(self.conf)
        await fm.send_message(message)

