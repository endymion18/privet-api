import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from starlette.responses import JSONResponse

from src.database import get_async_session
from src.users.exceptions import *
from src.users.models import User
from src.users.schemas import UserRegister, UserLogin
from src.users.utils import validate_user, hash_password, generate_confirmation_token, send_email, check_verification, \
    verify_user

auth_router = APIRouter(
    tags=["Auth"],
)

verify_router = APIRouter(
    tags=["Verification"]
)


@auth_router.post("/register",
                  status_code=status.HTTP_201_CREATED,
                  )
async def register(user_data: UserRegister, session: AsyncSession = Depends(get_async_session)):
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

    return JSONResponse(content={"Success": "User successfully created"}, status_code=status.HTTP_201_CREATED)


@auth_router.post("/login",
                  status_code=status.HTTP_200_OK
                  )
async def login(user_data: UserLogin = Depends(), session: AsyncSession = Depends(get_async_session)):
    email, password = user_data.user_email, user_data.password

    try:
        await verify_user(email, password, session)
    except WrongEmail as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)
    except NotVerified as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)
    except WrongPassword as error:
        return JSONResponse(content={"detail": error.__str__()}, status_code=status.HTTP_400_BAD_REQUEST)




@auth_router.post("/logout",
                  status_code=status.HTTP_201_CREATED
                  )
async def logout():
    pass

# переделать


@verify_router.post("/request-verify",
                    status_code=status.HTTP_202_ACCEPTED)
async def request_verify(email: str, session: AsyncSession = Depends(get_async_session)):
    await check_verification(email, session)
    token = await generate_confirmation_token()
    await send_email(email, token)
    return JSONResponse(content={"Verify token": token}, status_code=status.HTTP_202_ACCEPTED)


@verify_router.post("/verify-email",
                    status_code=status.HTTP_202_ACCEPTED)
async def verify_email(email: str, confirmation_token: str, user_token: str,
                       session: AsyncSession = Depends(get_async_session)):
    if confirmation_token == user_token:
        stmt = update(User).where(User.email == email).values(email_verified=True)
        await session.execute(stmt)
        await session.commit()
        return JSONResponse(content={"Success": "User verified"}, status_code=status.HTTP_202_ACCEPTED)
    else:
        return JSONResponse(content={"detail": "Wrong user token"}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
