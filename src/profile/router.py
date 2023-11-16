from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.auth.models import User
from src.auth.utils import get_current_user
from src.database import get_async_session
from src.profile.schemas import ChangeUserInfo
from src.profile.utils import get_user_profile, get_languages, update_user_info, get_countries, get_language, \
    get_languages_by_id, get_country_by_id

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
async def get_user_profile_info(current_user: User = Depends(get_current_user),
                                session: AsyncSession = Depends(get_async_session)):
    return await get_user_profile(current_user, session)


@profile_router.post("/users/me/profile/change",
                     status_code=status.HTTP_200_OK
                     )
async def change_user_profile_info(user_info: ChangeUserInfo,
                                   current_user: User = Depends(get_current_user),
                                   session: AsyncSession = Depends(get_async_session)):
    return await update_user_info(user_info, current_user, session)
    pass
