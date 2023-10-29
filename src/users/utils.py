from passlib.context import CryptContext

from email_validator import validate_email
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.exceptions import *
from src.users.models import User
from src.users.schemas import UserRegister

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def validate_user(user_data: UserRegister, session: AsyncSession):
    # Email validation

    stmt = await session.execute(select(User.email).where(User.email == user_data.email))
    stmt = stmt.scalar()
    if stmt is not None:
        raise UserAlreadyExists

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


