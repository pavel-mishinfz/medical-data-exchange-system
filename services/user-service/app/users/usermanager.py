import pathlib
import sys
import uuid
from typing import Optional, Union

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin, InvalidPasswordException

from .database import database, models
from . import secretprovider, schemas

from email.mime.text import MIMEText
from smtplib import SMTP_SSL

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
import config

cfg = config.load_config()


class UserManager(UUIDIDMixin, BaseUserManager[models.User, uuid.UUID]):

    async def validate_password(
        self,
        password: str,
        user: Union[schemas.user.UserCreate, models.User],
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Пароль должен содержать не менее 8 символов"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Пароль не должен содержать e-mail"
            )

    async def on_after_register(
            self, user: models.User, request: Optional[Request] = None
    ):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: models.User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: models.User, token: str, request: Optional[Request] = None
    ):
        message = make_html_template_msg(token)
        msg = MIMEText(message, "html")
        msg['Subject'] = 'Подтверждение регистрации'
        msg['From'] = cfg.own_email
        msg['To'] = user.email

        with SMTP_SSL("smtp.gmail.com", port=465) as server:
            server.login(cfg.own_email, cfg.own_email_password)
            server.send_message(msg)
            server.quit()


async def get_user_manager(
        user_db=Depends(database.get_user_db),
        secret_provider: secretprovider.SecretProvider = Depends(secretprovider.get_secret_provider)
):
    user_manager = UserManager(user_db)
    user_manager.reset_password_token_secret = secret_provider.reset_password_token_secret
    user_manager.verification_token_secret = secret_provider.verification_token_secret
    yield user_manager


def make_html_template_msg(token: str):
    return f"""
    <html>
        <body>
            <a href="http://127.0.0.1:8000/pass?token={token}">
                <button type="submit">Подтвердить регистрацию</button>
            </a>
        </body>
    </html>
    """
