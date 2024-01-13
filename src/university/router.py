from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette import status

from starlette.responses import JSONResponse

from src.database import get_async_session
from src.university.models import University, InstitutesURFU

university_router = APIRouter(
    tags=["University"]
)


@university_router.get("/getAllUniversities",
                       status_code=status.HTTP_200_OK)
async def get_all_universities(count: int, offset: int = 0,
                               session: AsyncSession = Depends(get_async_session)):
    stmt = await session.execute((select(University.name).limit(count).offset(offset)))
    results = stmt.all()

    response_dict = [{"name": name[0]}
                     for name in results]
    return JSONResponse({"details": response_dict})


@university_router.get("/institutes",
                       status_code=status.HTTP_200_OK)
async def get_urfu_institutes(session: AsyncSession = Depends(get_async_session)):
    stmt = await session.execute(select(InstitutesURFU))
    results = stmt.scalars().all()
    return results


@university_router.get("/institutes/{institute_id}",
                       status_code=status.HTTP_200_OK)
async def get_urfu_institute_by_id(institute_id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = await session.execute(select(InstitutesURFU).where(InstitutesURFU.id == institute_id))
    results = stmt.scalar()
    return results
