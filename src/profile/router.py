import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse, FileResponse

from src.auth.models import User
from src.auth.router import get_user_by_email
from src.auth.utils import get_current_user
from src.database import get_async_session
from src.profile.schemas import ChangeUserInfo
from src.profile.utils import get_user_profile, get_languages, update_user_info, get_countries, get_language, \
    get_languages_by_id, get_country_by_id, get_user_by_uuid

profile_router = APIRouter(
    tags=["Profiles"],
)


@profile_router.get("/languages",
                    status_code=status.HTTP_200_OK
                    )
async def get_all_languages(session: AsyncSession = Depends(get_async_session)):
    return await get_languages(session)


@profile_router.get("/languages/{language_id}",
                    status_code=status.HTTP_200_OK
                    )
async def get_language_by_id(language_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_language(language_id, session)


@profile_router.get("/languages/",
                    status_code=status.HTTP_200_OK
                    )
async def get_languages_by_ids(languages_ids: list[int] = Query(None),
                               session: AsyncSession = Depends(get_async_session)):
    return await get_languages_by_id(languages_ids, session)


@profile_router.get("/countries",
                    status_code=status.HTTP_200_OK
                    )
async def get_all_countries(session: AsyncSession = Depends(get_async_session)):
    return await get_countries(session)


@profile_router.get("/countries/{country_id}",
                    status_code=status.HTTP_200_OK
                    )
async def get_all_countries(country_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_country_by_id(country_id, session)


@profile_router.get("/users/me/profile",
                    status_code=status.HTTP_200_OK
                    )
async def get_my_profile_info(current_user: User = Depends(get_current_user),
                              session: AsyncSession = Depends(get_async_session)):
    return await get_user_profile(current_user, session)


@profile_router.get("/users/{email}",
                    status_code=status.HTTP_200_OK
                    )
async def get_user_profile_info_by_email(email: str,
                                         session: AsyncSession = Depends(get_async_session)):
    user = await get_user_by_email(email, session)
    if isinstance(user, JSONResponse):
        return user
    return await get_user_profile(user, session)


@profile_router.get("/users/by-id/{user_id}",
                    status_code=status.HTTP_200_OK
                    )
async def get_user_profile_info_by_id(user_id: uuid.UUID,
                                      session: AsyncSession = Depends(get_async_session)):
    user = await get_user_by_uuid(user_id, session)
    if user is None:
        return JSONResponse(content={"detail": "User does not exist"}, status_code=status.HTTP_400_BAD_REQUEST)
    return await get_user_profile(user, session)


@profile_router.post("/users/me/profile/change",
                     status_code=status.HTTP_200_OK
                     )
async def change_user_profile_info(user_info: ChangeUserInfo,
                                   current_user: User = Depends(get_current_user),
                                   session: AsyncSession = Depends(get_async_session)):
    return await update_user_info(user_info, current_user, session)


@profile_router.post("/users/me/profile/avatar/upload",
                     status_code=status.HTTP_200_OK
                     )
async def change_user_avatar(avatar: UploadFile = File(...), current_user: User = Depends(get_current_user),
                             session: AsyncSession = Depends(get_async_session)):

    pass


@profile_router.get("/images/{path}")
async def get_image(path: str):
    parent_dir_path = os.path.dirname(__file__)
    img_path = Path("Python/privet-api/avatars/44423234234.jpg")
    return parent_dir_path
