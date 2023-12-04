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
from src.profile.models import Student


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
    arrival_date = await session.execute(select(Student.arrival_date).where(Student.user_id == user_id))
    arrival_date = arrival_date.scalar()
    if arrival_date is not None:
        arrival_date = datetime(arrival_date.year, arrival_date.month, arrival_date.day)
    visa_expiration = await session.execute(select(Student.visa_expiration).where(Student.user_id == user_id))
    visa_expiration = visa_expiration.scalar()
    if visa_expiration is not None:
        visa_expiration = datetime(visa_expiration.year, visa_expiration.month, visa_expiration.day)
    result = TaskSchema(result, visa_expiration, arrival_date)
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
    arrival_date = await session.execute(select(Student.arrival_date).where(Student.user_id == user_id))
    arrival_date = arrival_date.scalar()
    if arrival_date is not None:
        arrival_date = datetime(arrival_date.year, arrival_date.month, arrival_date.day)
    visa_expiration = await session.execute(select(Student.visa_expiration).where(Student.user_id == user_id))
    visa_expiration = visa_expiration.scalar()
    if visa_expiration is not None:
        visa_expiration = datetime(visa_expiration.year, visa_expiration.month, visa_expiration.day)
    result = TaskSchema(result, visa_expiration, arrival_date)
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
