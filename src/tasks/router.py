from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from starlette import status

from starlette.responses import JSONResponse

from src.database import get_async_session
from src.auth.utils import get_current_user
from src.auth.models import User
import uuid
from src.tasks.models import Task, TaskOperation, SetTask

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

    return result.as_dict()


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

    return result.as_dict()

# test=UUID: 8d4b6d8b-0356-4a66-8d2c-6bbd4fdbbe2b


@tasks_router.post("/users/tasks/change",
                   status_code=status.HTTP_200_OK)
async def set_user_tasks(tasks: SetTask,
                         session: AsyncSession = Depends(get_async_session)):
    approved_tasks = []
    for changed_task in tasks.tasks:
        if changed_task.name in Task.__table__.columns:
            approved_tasks.append(changed_task)

    stmt = await session.execute(select(Task).where(Task.user_id == tasks.user_id))
    result = stmt.fetchone()[0]

    for task in approved_tasks:
        setattr(result, task.name, task.value)
    await session.commit()

    return JSONResponse({"details": "ok"})
