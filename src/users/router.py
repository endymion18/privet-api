import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from starlette.responses import JSONResponse

from src.database import get_async_session
from src.users.exceptions import *
from src.users.models import User
from src.users.schemas import UserRegister
from src.users.utils import validate_user, hash_password

auth_router = APIRouter(
    tags=["Auth"],
)


@auth_router.post("/register",
                  status_code=201)
async def register(user_data: UserRegister, session: AsyncSession = Depends(get_async_session)):
    # Validate user data

    try:
        await validate_user(user_data, session)
    except UserAlreadyExists:
        return JSONResponse(content={"Wrong email": "Email already exists"}, status_code=400)
    except InvalidPassword as error:
        return JSONResponse(content={"Wrong password": error.__str__()}, status_code=400)
    except ValueError as error:
        return JSONResponse(content={"Wrong email": error.__str__()}, status_code=422)

    # Password hashing

    user_data.password = await hash_password(user_data.password)

    # Add user to DB

    stmt = insert(User).values(id=uuid.uuid4(),
                               email=user_data.email,
                               hashed_password=user_data.password,
                               role_id=user_data.role_id)
    await session.execute(stmt)
    await session.commit()

    return JSONResponse(content={"Success": "User successfully created"}, status_code=201)
