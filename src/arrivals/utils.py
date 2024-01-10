import datetime
import uuid

from sqlalchemy import update, insert, select, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import and_
from starlette.responses import JSONResponse

from src.arrivals.models import Arrival, ArrivalParticipants, ArrivalInvitations
from src.arrivals.schemas import StudentArrivalData, InvitedStudentData, FormattedArrival, StudentArrivalDataSchema, \
    BuddyArrivalSchema, BuddySchema
from src.auth.models import User
from src.auth.router import get_user_by_email
from src.messenger.models import Chat, Message
from src.profile.models import Student, Contacts, Buddy
from src.profile.router import get_user_profile_info_by_email


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


async def check_current_arrival(user_email: str, session: AsyncSession) -> bool:
    arrival = await session.execute(
        select(ArrivalParticipants).where(and_(ArrivalParticipants.participant_email == user_email,
                                               ArrivalParticipants.participant_role == 1)))
    arrival = arrival.scalar()

    return False if arrival is None else True


async def get_all_arrivals_dict(session: AsyncSession) -> dict:
    current_datetime = datetime.datetime.utcnow()

    past_arrivals = await session.execute(
        select(Arrival).where(Arrival.arrival_date < current_datetime).order_by(Arrival.arrival_date.desc()))

    future_arrivals = await session.execute(
        select(Arrival).where(Arrival.arrival_date >= current_datetime).order_by(Arrival.arrival_date))

    return {
        "past_arrivals": past_arrivals.scalars().all(),
        "future_arrivals": future_arrivals.scalars().all()
    }


async def get_buddy_arrivals(user_email: str, session: AsyncSession):
    arrivals = await session.execute(
        select(Arrival).join(ArrivalParticipants, ArrivalParticipants.arrival_id == Arrival.id).where(
            ArrivalParticipants.participant_email == user_email).order_by(Arrival.arrival_date.desc()))

    return arrivals.scalars().all()


async def get_arrival_data_by_id(arrival_id: int, session: AsyncSession):
    arrival_info = await session.execute(select(Arrival).where(Arrival.id == arrival_id))
    arrival_info = arrival_info.scalar()
    participants = await session.execute(
        select(ArrivalParticipants).where(ArrivalParticipants.arrival_id == arrival_id))
    participants = participants.scalars().all()
    students = []
    buddies = []
    for participant in participants:
        profile = await get_user_profile_info_by_email(participant.participant_email, session)
        if participant.participant_role == 1:
            students.append(StudentArrivalDataSchema(profile, arrival_info))
        else:
            buddies.append(BuddyArrivalSchema(profile))
    return {
        "students": students,
        "buddies": buddies
    }


async def format_arrivals_list(arrivals_list: list, session: AsyncSession) -> list:
    for i in range(len(arrivals_list)):
        arrival = arrivals_list[i]

        participants = await session.execute(
            select(ArrivalParticipants).where(ArrivalParticipants.arrival_id == arrival.id))
        participants = participants.scalars().all()

        students = [await get_user_profile_info_by_email(participant.participant_email, session) for participant in participants
                    if participant.participant_role == 1]
        students_full_names = [student["profile_info"].full_name for student in students]
        students_countries = [student["profile_info"].citizenship for student in students]

        students_count = sum(1 for participant in participants if participant.participant_role == 1)
        buddies_count = sum(1 for participant in participants if participant.participant_role == 2)

        required_buddies = 2 if students_count >= 3 else 1
        buddies_amount = f"{buddies_count}/{required_buddies}"

        arrivals_list[i] = FormattedArrival(arrival, students_full_names, students_countries, buddies_amount)
    return arrivals_list


async def get_buddies(session: AsyncSession):
    buddies = await session.execute(select(Buddy).order_by(Buddy.full_name))
    buddies = buddies.scalars().all()
    buddies = [BuddySchema(buddy) for buddy in buddies]
    return buddies


async def add_buddy(user_id: uuid.UUID, arrival_id: int, session: AsyncSession):
    email = await session.execute(select(User.email).where(User.id == user_id))
    email = email.scalar()
    buddy_in_arrival = await session.execute(select(ArrivalParticipants).where(
        and_(ArrivalParticipants.arrival_id == arrival_id, ArrivalParticipants.participant_email == email)))
    buddy_in_arrival = buddy_in_arrival.scalar()
    if buddy_in_arrival is None:
        await session.execute(insert(ArrivalParticipants).values(arrival_id=arrival_id,
                                                                 participant_role=2,
                                                                 participant_email=email))
        await session.commit()
        return True
    return False


async def confirm_arrival(arrival_id: int, session: AsyncSession):
    await session.execute(update(Arrival).where(Arrival.id == arrival_id).values(
        confirmed=True
    ))
    await session.commit()


async def delete_buddy(user_id: uuid.UUID, arrival_id: int, session: AsyncSession):
    email = await session.execute(select(User.email).where(User.id == user_id))
    email = email.scalar()
    buddy_in_arrival = await session.execute(select(ArrivalParticipants).where(
        and_(ArrivalParticipants.arrival_id == arrival_id, ArrivalParticipants.participant_email == email)))
    buddy_in_arrival = buddy_in_arrival.scalar()
    if buddy_in_arrival is not None:
        await session.execute(delete(ArrivalParticipants).where(
            and_(ArrivalParticipants.arrival_id == arrival_id, ArrivalParticipants.participant_email == email)))
        await session.commit()
        return True
    return False


async def get_students_ids(arrival_id: int, session: AsyncSession):
    student_emails = await session.execute(
        select(ArrivalParticipants.participant_email).where(and_(ArrivalParticipants.arrival_id == arrival_id,
                                                                 ArrivalParticipants.participant_role == 1)))
    student_emails = student_emails.scalars().all()

    student_ids = []
    for email in student_emails:
        user = await get_user_by_email(email, session)
        if not isinstance(user, JSONResponse):
            student_ids.append(user.id)
    return student_ids


async def delete_chat(first_user: uuid.UUID, second_user: uuid.UUID, session: AsyncSession):
    stmt = await session.execute(select(Chat).where(or_(and_(Chat.first_user == first_user,
                                                             Chat.second_user == second_user),
                                                        and_(Chat.first_user == second_user,
                                                             Chat.second_user == first_user
                                                             ))))
    chats = stmt.scalars().all()

    for chat in chats:
        await session.execute(delete(Message).where(Message.chat_id == chat.id))
        await session.execute(delete(Chat).where(Chat.id == chat.id))

    await session.commit()
