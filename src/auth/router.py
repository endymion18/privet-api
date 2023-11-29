import uuid

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from starlette.responses import JSONResponse

from src.database import get_async_session
from src.auth.exceptions import *
from src.auth.models import User
from src.auth.schemas import UserRegister, ChangePassword, VerifyEmail, ForgotPassword
from src.auth.utils import validate_user, hash_password, verify_user, encode_jwt_token, get_current_user, \
    validate_password, verify_password
from src.auth.verify_email import send_token, check_token

auth_router = APIRouter(
    tags=["Users"],
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
        user_data.password = await hash_password(user_data.password)
        stmt = insert(User).values(id=uuid.uuid4(),
                                   email=user_data.email,
                                   hashed_password=user_data.password,
                                   role_id=user_data.role_id)
    except (UserAlreadyExists, InvalidPassword) as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)
    except ValueError as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except NotVerified:
        user_data.password = await hash_password(user_data.password)
        stmt = update(User).where(User.email == user_data.email) \
            .values(id=uuid.uuid4(),
                    hashed_password=user_data.password,
                    role_id=user_data.role_id)

    # Add user to DB

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


@auth_router.get("/auth/me",
                 status_code=status.HTTP_200_OK
                 )
async def get_current_user_data(current_user: User = Depends(get_current_user)):
    return current_user


@auth_router.get("/auth/get-user/{email}",
                 status_code=status.HTTP_200_OK
                 )
async def get_user_by_email(email: str, session: AsyncSession = Depends(get_async_session)):
    user = await session.execute(select(User).where(User.email == email))
    user = user.scalar()
    if user is not None:
        return user
    return JSONResponse(content={"detail": "User does not exist"}, status_code=status.HTTP_400_BAD_REQUEST)


@auth_router.patch("/auth/forgot-password",
                   status_code=status.HTTP_200_OK
                   )
async def change_password_on_forgot(info: ForgotPassword, session: AsyncSession = Depends(get_async_session)):
    new_hashed_password = await hash_password(info.new_password)
    stmt = update(User).where(User.email == info.email).values(hashed_password=new_hashed_password)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(content={"detail": "Password successfully changed"}, status_code=status.HTTP_200_OK)


@auth_router.patch("/auth/me/change-password",
                   status_code=status.HTTP_200_OK
                   )
async def change_password(pass_info: ChangePassword,
                          current_user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_async_session)):
    if pass_info.new_password == pass_info.old_password:
        return JSONResponse(content={"detail": "Passwords are the same"}, status_code=status.HTTP_400_BAD_REQUEST)
    try:
        await validate_password(pass_info.new_password)
        old_hashed_password = await session.execute(select(User.hashed_password)
                                                    .where(User.id == current_user.id))
        old_hashed_password = old_hashed_password.scalar()
        new_hashed_password = await verify_password(old_hashed_password, pass_info.old_password, pass_info.new_password)
    except (InvalidPassword, WrongPassword) as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)

    stmt = update(User).where(User.email == current_user.email) \
        .values(hashed_password=new_hashed_password)

    await session.execute(stmt)
    await session.commit()

    return JSONResponse(content={"detail": "Password was successfully changed"}, status_code=status.HTTP_200_OK)


@verify_router.post("/send-verification-token/{email}",
                    status_code=status.HTTP_200_OK)
async def send_verification_token(email: str,
                                  session: AsyncSession = Depends(get_async_session)):
    try:
        await send_token(email, session)
    except WrongEmail as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(content={"detail": "Token has been sent"}, status_code=status.HTTP_200_OK)


@verify_router.post("/verify-email",
                    status_code=status.HTTP_202_ACCEPTED)
async def verify_email(verification: VerifyEmail,
                       session: AsyncSession = Depends(get_async_session)):
    try:
        await check_token(verification.email, verification.token, session)
    except WrongToken as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(content={"detail": "Token is accepted"}, status_code=status.HTTP_202_ACCEPTED)
