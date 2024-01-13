import os
import random
import smtplib

from email.message import EmailMessage

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from passlib.context import CryptContext

from jose import jwt

from email_validator import validate_email
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.auth.exceptions import *
from src.auth.models import User
from src.auth.schemas import UserRegister

# constants

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

numbers = "0123456789"

email_from = os.environ.get("EMAIL_ADDRESS_FROM")
email_password = os.environ.get("EMAIL_PASSWORD")
secret_key = os.environ.get("SECRET_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", scheme_name="Bearer")


async def validate_user(user_data: UserRegister, session: AsyncSession):
    # Email validation

    user_from_db = await session.execute(select(User).where(User.email == user_data.email))
    user_from_db = user_from_db.scalar()
    if user_from_db is not None:
        if user_from_db.email_verified:
            raise UserAlreadyExists("User already exist")
        raise NotVerified

    # Set check_deliverability to True to check if email can get messages

    validate_email(user_data.email, check_deliverability=False)

    # Password validation
    await validate_password(user_data.password)


async def validate_password(password: str):
    if len(password) < 8:
        raise InvalidPassword("Password must be longer than 8 characters")
    # Можно будет дописать валидацию пароля (чтобы пароль обязательно содержал цифры, спец. символы и тд)


async def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def verify_password(hashed_password: str, old_password: str, new_password: str) -> str:
    is_password_correct = pwd_context.verify(old_password, hashed_password)
    if not is_password_correct:
        raise WrongPassword("Password is incorrect")
    new_hashed_password = await hash_password(new_password)
    return new_hashed_password


async def generate_confirmation_token() -> str:
    result_str = ''.join(random.choice(numbers) for i in range(6))
    return result_str


async def send_email(email_to: str, code: str):
    msg = EmailMessage()
    msg['Subject'] = 'Mail confirmation'
    msg['From'] = email_from
    msg['To'] = email_to

    with open('../src/auth/message.html') as html:
        text = html.read()
    text = text.replace('000000', code)
    text = text.replace('zaglushka@gmail.com', email_to)
    msg.set_content(text, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(email_from, email_password)
        server.send_message(msg)


async def verify_user(email: str, password: str, session: AsyncSession):
    email_from_db = await session.execute(select(User.email).where(User.email == email))
    if email_from_db.scalar() is None:
        raise WrongEmail("This user does not exist")

    hashed_password = await session.execute(select(User.hashed_password).where(User.email == email))
    if not pwd_context.verify(password, hashed_password.scalar()):
        raise WrongPassword("Password is incorrect")

    is_user_verified = await session.execute(select(User.email_verified).where(User.email == email))
    if not is_user_verified.scalar():
        raise NotVerified("This user is not verified")


async def encode_jwt_token(data: dict):
    jwt_token = jwt.encode(data, secret_key, "HS256")
    return jwt_token


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_async_session)):
    decoded_token = jwt.decode(token, secret_key, ["HS256"])
    email = decoded_token.get("sub")
    stmt = await session.execute(select(User).where(User.email == email))
    return stmt.scalar()
