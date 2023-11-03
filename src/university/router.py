import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette import status

from starlette.responses import JSONResponse

from src.database import get_async_session
from src.university.models import University

university_router = APIRouter(
    tags=["University"]
)


@university_router.get("/getAllUniversities",
                       status_code=status.HTTP_200_OK)
async def get_all_universities(count: int, offset: int = 0,
                               session: AsyncSession = Depends(get_async_session)):
    stmt = await session.execute((select(University).limit(count).offset(offset)))
    results = stmt.all()
    print(results)
    response_dict = [{"id": university[0].id, "name": university[0].name}
                     for university in results]
    return JSONResponse({"details": response_dict})

