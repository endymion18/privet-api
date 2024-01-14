from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from starlette import status

from starlette.responses import JSONResponse

from src.database import get_async_session
from src.auth.utils import get_current_user
from src.auth.models import User
from src.tasks.schemas import TaskSchema
from src.tasks.models import Task
from src.arrivals.models import ArrivalParticipants
from datetime import datetime
from src.profile.models import Student

tasks_router = APIRouter(
    tags=["Tasks"]
)


@tasks_router.get("/users/me/tasks",
                  status_code=status.HTTP_200_OK)
async def get_current_user_tasks(current_user: User = Depends(get_current_user),
                                 session: AsyncSession = Depends(get_async_session)):
    if current_user.role_id == 1:
        user_id = current_user.id
        stmt = await session.execute(select(Task).where(Task.user_id == user_id))
        result = stmt.scalar()
        stmt = await session.execute(select(ArrivalParticipants.arrival_id)
                                     .where(ArrivalParticipants.participant_email == current_user.email))
        arrival_id = stmt.scalar()
        if arrival_id is None:
            return JSONResponse({"error": "not an arrival participant"})
        if result is None:
            result = await session.execute(insert(Task).values(user_id=user_id, arrival_id=arrival_id).returning(Task))
            result = result.scalar()
            await session.commit()
        arrival_date = await session.execute(select(Student.arrival_date).where(Student.user_id == user_id))
        arrival_date = arrival_date.scalar()
        email = current_user.email
        if arrival_date is not None:
            arrival_date = datetime(arrival_date.year, arrival_date.month, arrival_date.day)
        visa_expiration = await session.execute(select(Student.visa_expiration).where(Student.user_id == user_id))
        visa_expiration = visa_expiration.scalar()
        if visa_expiration is not None:
            visa_expiration = datetime(visa_expiration.year, visa_expiration.month, visa_expiration.day)
        fullname = 'me'
        if current_user.role_id == 1:
            stmt = await session.execute(select(Student.full_name).where(Student.user_id == current_user.id))
            fullname = stmt.scalar()
        result = TaskSchema(result, visa_expiration, arrival_date, email, fullname)
        return result
    else:
        return JSONResponse({"error": "you are not a student"})


@tasks_router.get("/arrivals/tasks/",
                  status_code=status.HTTP_200_OK)
async def get_arrival_tasks(arrival_id: int, session: AsyncSession = Depends(get_async_session)):
    arrival_participants = await session.execute(select(ArrivalParticipants)
                                                 .where(ArrivalParticipants.arrival_id == arrival_id))
    arrival_participants = arrival_participants.fetchall()
    if arrival_participants is None:
        return JSONResponse({"details": "no participants found"}, status_code=400)
    tasks = []
    for participant in arrival_participants:
        if participant[0].participant_role == 1:
            user_id = await session.execute(select(User.id).where(User.email == participant[0].participant_email))
            user_id = user_id.scalar()
            stmt = await session.execute(select(Student.full_name).where(Student.user_id == user_id))
            fullname = stmt.scalar()
            participant_tasks = await session.execute(select(Task).where(Task.user_id == user_id))
            participant_tasks = participant_tasks.scalar()
            arrival_date = await session.execute(select(Student.arrival_date).where(Student.user_id == user_id))
            arrival_date = arrival_date.scalar()
            if arrival_date is not None:
                arrival_date = datetime(arrival_date.year, arrival_date.month, arrival_date.day)
            visa_expiration = await session.execute(select(Student.visa_expiration).where(Student.user_id == user_id))
            visa_expiration = visa_expiration.scalar()
            if visa_expiration is not None:
                visa_expiration = datetime(visa_expiration.year, visa_expiration.month, visa_expiration.day)
            result = TaskSchema(participant_tasks, visa_expiration, arrival_date, participant[0].participant_email,
                                fullname)
            tasks.append(result)
    return tasks


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
