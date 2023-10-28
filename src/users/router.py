import uuid

from email_validator import validate_email

from fastapi import APIRouter, Depends
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from starlette import status
from starlette.responses import JSONResponse

from src.database import get_async_session
from src.users.models import User
from src.users.schemas import UserRegister
from src.users.utils import email_exist

auth_router = APIRouter(
    tags=["Auth"],
)

# сделать метод


@auth_router.post("/register",
                  status_code=201,
                  responses={
                        status.HTTP_422_UNPROCESSABLE_ENTITY: {}
                  })
async def register(user_data: UserRegister, session: AsyncSession = Depends(get_async_session)):
    # Email validation

    if await email_exist(user_data.email, session):
        return JSONResponse(content={"Wrong email": "Email already exists"}, status_code=422)

    try:
        # Validate email without deliverability check (изменить на True, чтобы проверять что домен рабочий
        # (работает медленно))
        validate_email(user_data.email, check_deliverability=False)
    except ValueError as e:
        error = e.__str__()
        return JSONResponse(content={"Wrong email": error}, status_code=400)

    # Password hashing

    #user_data.password =
    stmt = insert(User).values(id=uuid.uuid4(),
                               email=user_data.email,
                               hashed_password=user_data.password,
                               role_id=user_data.role_id)
    await session.execute(stmt)
    await session.commit()
    return status.HTTP_201_CREATED
