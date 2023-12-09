import datetime

from sqlalchemy import update, insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import and_

from src.arrivals.models import Arrival, ArrivalParticipants, ArrivalInvitations
from src.arrivals.schemas import StudentArrivalData, InvitedStudentData
from src.auth.models import User
from src.profile.models import Student, Contacts


async def update_profile_by_arrival(arrival_data: StudentArrivalData,
                                    current_user: User,
                                    session: AsyncSession):
    arrival_date = datetime.datetime.fromisoformat(f'{arrival_data.arrival_date}T{arrival_data.arrival_time}')

    await session.execute(update(Student).where(Student.user_id == current_user.id).values(
        full_name=arrival_data.full_name,
        sex=arrival_data.sex,
        citizenship=arrival_data.citizenship,
        arrival_date=arrival_date
    ))

    await session.execute(update(Contacts).where(Contacts.user_id == current_user.id).values(
        phone=arrival_data.phone,
        telegram=arrival_data.telegram,
        whatsapp=arrival_data.whatsapp,
        vk=arrival_data.vk
    ))

    await session.commit()


async def update_profile_by_invitation(student_data: InvitedStudentData,
                                       arrival_data: Arrival,
                                       current_user: User,
                                       session: AsyncSession):
    await session.execute(update(Student).where(Student.user_id == current_user.id).values(
        full_name=student_data.full_name,
        sex=student_data.sex,
        citizenship=student_data.citizenship,
        arrival_date=arrival_data.arrival_date
    ))

    await session.execute(update(Contacts).where(Contacts.user_id == current_user.id).values(
        phone=student_data.phone,
        telegram=student_data.telegram,
        whatsapp=student_data.whatsapp,
        vk=student_data.vk
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


async def delete_student_from_invitation_table(user_email: str, session: AsyncSession):
    await session.execute(delete(ArrivalInvitations).where(ArrivalInvitations.student_email == user_email))
    await session.commit()


async def add_student_to_invites(arrival_id: int, student_email: str, session: AsyncSession):
    await session.execute(insert(ArrivalInvitations).values(
        arrival_id=arrival_id,
        student_email=student_email
    ))

    await session.commit()


async def check_invitation_in_db(user_email: str, session: AsyncSession):
    invitation = await session.execute(select(ArrivalInvitations).where(ArrivalInvitations.student_email == user_email))
    invitation = invitation.scalar()
    if invitation is None:
        return invitation

    arrival = await session.execute(select(Arrival).where(Arrival.id == invitation.arrival_id))

    return arrival.scalar()


async def check_current_arrival(user_email: str, session: AsyncSession):
    arrival = await session.execute(
        select(ArrivalParticipants).where(and_(ArrivalParticipants.participant_email == user_email,
                                               ArrivalParticipants.participant_role == 1)))
    arrival = arrival.scalar()

    return False if arrival is None else True

