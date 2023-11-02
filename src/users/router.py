import uuid

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from starlette.responses import JSONResponse

from src.database import get_async_session
from src.users.exceptions import *
from src.users.models import User
from src.users.schemas import UserRegister
from src.users.utils import validate_user, hash_password, verify_user, encode_jwt_token, get_current_user
from src.users.verify_email import send_token, check_token

auth_router = APIRouter(
    tags=["Auth"],
)

verify_router = APIRouter(
    tags=["Verification"]
)


@auth_router.post("/register",
                  status_code=status.HTTP_201_CREATED,
                  )
async def register(user_data: UserRegister,
                   session: AsyncSession = Depends(get_async_session)):
    # Validate user data

    try:
        await validate_user(user_data, session)
    except UserAlreadyExists:
        return JSONResponse(content={"detail": "Email already exists"}, status_code=status.HTTP_400_BAD_REQUEST)
    except InvalidPassword as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)
    except ValueError as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Password hashing

    user_data.password = await hash_password(user_data.password)

    # Add user to DB

    stmt = insert(User).values(id=uuid.uuid4(),
                               email=user_data.email,
                               hashed_password=user_data.password,
                               role_id=user_data.role_id)
    await session.execute(stmt)
    await session.commit()

    return JSONResponse(content={"detail": "User successfully created"}, status_code=status.HTTP_201_CREATED)


@auth_router.post("/login",
                  status_code=status.HTTP_200_OK
                  )
async def login(user_data: OAuth2PasswordRequestForm = Depends(),
                session: AsyncSession = Depends(get_async_session)):
    email, password = user_data.username, user_data.password

    try:
        await verify_user(email, password, session)
    except (WrongEmail, NotVerified, WrongPassword) as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)

    jwt_token = await encode_jwt_token({"sub": email})
    return {"access_token": jwt_token,
            "token_type": "bearer"}


@verify_router.post("/send-verification-token",
                    status_code=status.HTTP_200_OK)
async def send_verification_token(email: str,
                                  session: AsyncSession = Depends(get_async_session)):
    try:
        await send_token(email, session)
    except (AlreadyVerified, WrongEmail) as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(content={"detail": "Token has been sent"}, status_code=status.HTTP_200_OK)


@verify_router.post("/verify-email",
                    status_code=status.HTTP_202_ACCEPTED)
async def verify_email(email: str,
                       token: str,
                       session: AsyncSession = Depends(get_async_session)):
    try:
        await check_token(email, token, session)
    except (AlreadyVerified, WrongEmail, WrongToken) as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(content={"detail": "Token is accepted"}, status_code=status.HTTP_202_ACCEPTED)
