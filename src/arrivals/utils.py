import datetime

from sqlalchemy import update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.arrivals.models import Arrival, ArrivalParticipants
from src.arrivals.schemas import StudentArrivalData
from src.auth.models import User
from src.profile.models import Student, Contacts


async def update_profile_by_arrival(arrival_data: StudentArrivalData, current_user: User, session: AsyncSession):
    await session.execute(update(Student).where(Student.user_id == current_user.id).values(
        full_name=arrival_data.full_name,
        sex=arrival_data.sex
    ))

    await session.execute(update(Contacts).where(Contacts.user_id == current_user.id).values(
        phone=arrival_data.phone,
        telegram=arrival_data.telegram,
        whatsapp=arrival_data.whatsapp,
        vk=arrival_data.vk
    ))

    await session.commit()


async def submit_arrival(arrival_data: StudentArrivalData, session: AsyncSession):
    arrival_date = datetime.datetime.fromisoformat(f'{arrival_data.arrival_date}T{arrival_data.arrival_time}')

    arrival_id = await session.execute(insert(Arrival).values(
        arrival_date=arrival_date,
        flight_number=arrival_data.flight_number,
        arrival_point=arrival_data.arrival_point,
        comment=arrival_data.comment,
        tickets=arrival_data.tickets
    ).returning(Arrival.id))

    await session.commit()

    return arrival_id.scalar()


async def add_student_to_arrival(arrival_id: int, student_email: str, session: AsyncSession):
    await session.execute(insert(ArrivalParticipants).values(
        arrival_id=arrival_id,
        participant_email=student_email,
        participant_role=1
    ))

    await session.commit()
