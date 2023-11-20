from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from starlette import status

from starlette.responses import JSONResponse

from src.database import get_async_session

import uuid
from src.tasks.models import Task, TaskOperation, SetTask

tasks_router = APIRouter(
    tags=["Tasks"]
)


@tasks_router.get("/get-user-tasks",
                  status_code=status.HTTP_200_OK)
async def get_user_tasks(user_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    stmt = await session.execute(select(Task).where(Task.user_id == user_id))
    result = stmt.fetchone()[0]

    return JSONResponse({"details": result.as_dict()})


# test=UUID: 8d4b6d8b-0356-4a66-8d2c-6bbd4fdbbe2b


@tasks_router.post("/set-user-tasks",
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
