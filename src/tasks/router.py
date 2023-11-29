from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from starlette import status

from starlette.responses import JSONResponse

from src.database import get_async_session
from src.auth.utils import get_current_user
from src.auth.models import User
from src.tasks.schemas import TaskSchema
from src.tasks.models import Task, SetTask
from datetime import datetime


tasks_router = APIRouter(
    tags=["Tasks"]
)


@tasks_router.get("/users/me/tasks",
                  status_code=status.HTTP_200_OK)
async def get_current_user_tasks(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    user_id = current_user.id
    stmt = await session.execute(select(Task).where(Task.user_id == user_id))
    result = stmt.scalar()
    if result is None:
        await session.execute(insert(Task).values(user_id=user_id))
        await session.commit()
        return JSONResponse({"details": "tasks created"})
    result = TaskSchema(result, datetime(2023, 11, 13), datetime(2023, 10, 10))
    return result


@tasks_router.get("/users/tasks/{email}",
                  status_code=status.HTTP_200_OK)
async def get_user_tasks(email: str, session: AsyncSession = Depends(get_async_session)):
    user_id = await session.execute(select(User.id).where(User.email == email))
    user_id = user_id.scalar()
    if user_id is None:
        return JSONResponse({"details": "wrong email"}, status_code=400)
    stmt = await session.execute(select(Task).where(Task.user_id == user_id))
    result = stmt.scalar()
    if result is None:
        await session.execute(insert(Task).values(user_id=user_id))
        await session.commit()
        return JSONResponse({"details": "tasks created"})
    result = TaskSchema(result, datetime(2023, 11, 13), datetime(2023, 10, 10))
    return result

# test=UUID: 8d4b6d8b-0356-4a66-8d2c-6bbd4fdbbe2b


@tasks_router.post("/users/tasks/change/{email}",
                   status_code=status.HTTP_200_OK)
async def set_user_tasks(task_name: str, task_value: bool, email: str,
                         session: AsyncSession = Depends(get_async_session)):
    if task_name not in Task.__table__.columns:
        return JSONResponse({"details": "wrong task name"}, status_code=400)

    user_id = await session.execute(select(User.id).where(User.email == email))
    user_id = user_id.scalar()
    if user_id is None:
        return JSONResponse({"details": "wrong email"}, status_code=400)

    stmt = await session.execute(select(Task).where(Task.user_id == user_id))
    result = stmt.fetchone()[0]
    setattr(result, task_name, task_value)
    await session.commit()

    return JSONResponse({"details": "ok"})
