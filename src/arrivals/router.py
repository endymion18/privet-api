from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from src.arrivals.schemas import ArrivalData, InvitedStudentData, AddBuddyToArrivalSchema
from src.arrivals.utils import update_profile_by_arrival, submit_arrival, add_student_to_invites, \
    add_student_to_arrival, check_invitation_in_db, update_profile_by_invitation, delete_student_from_invitation_table, \
    check_current_arrival, get_all_arrivals_dict, format_arrivals_list, get_arrival_data_by_id, get_buddies, add_buddy, \
    confirm_arrival, delete_buddy, get_buddy_arrivals, get_students_ids, delete_chat, check_active_arrival, \
    add_last_arrival_to_buddy, delete_last_arrival_from_buddy
from src.auth.models import User
from src.auth.utils import get_current_user
from src.database import get_async_session
from src.messenger.router import create_chat
from src.profile.router import get_user_profile_info_by_email
from src.profile.schemas import BuddyProfile
from src.students.utils import add_student_to_table, delete_student_from_table

arrival_router = APIRouter(
    tags=["Arrivals"],
)

teamleader_router = APIRouter(
    tags=["TeamleaderFunctions"],
)


@arrival_router.get("/check-payment/{email}",
                    status_code=status.HTTP_200_OK
                    )
async def check_payment(email: str,
                        session: AsyncSession = Depends(get_async_session)):
    user_profile = await get_user_profile_info_by_email(email, session)

    if isinstance(user_profile, JSONResponse):
        return user_profile

    if isinstance(user_profile["profile_info"], BuddyProfile):
        return JSONResponse(content={"detail": "You can't invite Buddy to arrival"},
                            status_code=status.HTTP_400_BAD_REQUEST)
    return user_profile["profile_info"].escort_paid


@arrival_router.post("/users/me/book-arrival",
                     status_code=status.HTTP_200_OK
                     )
async def book_new_arrival(arrival_data: ArrivalData,
                           current_user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_async_session)):
    if await check_current_arrival(current_user.email, session):
        return JSONResponse(content={"detail": f"User has already booked arrival"},
                            status_code=400)
    arrival_organizer = arrival_data.student_data
    await update_profile_by_arrival(arrival_organizer, current_user, session)

    arrival_id = await submit_arrival(arrival_organizer, session)
    await add_student_to_arrival(arrival_id, current_user.email, session)

    for email in arrival_data.invite:
        if email == current_user.email:
            return JSONResponse(content={"detail": f"User can't invite themself"},
                                status_code=400)

        if await check_current_arrival(email, session):
            return JSONResponse(content={"detail": f"User {email} has already booked arrival"},
                                status_code=400)

        invitation = await check_invitation_in_db(email, session)
        if invitation is None:
            await add_student_to_invites(arrival_id, email, session)
        else:
            return JSONResponse(content={"detail": f"User {email} has already been invited to arrival"},
                                status_code=400)

    return JSONResponse(content={"detail": "Arrival has been booked"}, status_code=200)


@arrival_router.get("/users/me/check-invitation",
                    status_code=status.HTTP_200_OK
                    )
async def check_invitation(current_user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_async_session)):
    arrival_data = await check_invitation_in_db(current_user.email, session)
    if arrival_data is None:
        return None

    return arrival_data


@arrival_router.post("/users/me/submit-invitation",
                     status_code=status.HTTP_200_OK
                     )
async def submit_invitation(student_data: InvitedStudentData,
                            current_user: User = Depends(get_current_user),
                            session: AsyncSession = Depends(get_async_session)):
    arrival_data = await check_invitation(current_user, session)

    if arrival_data is None:
        return JSONResponse(content={"detail": "User hasn't been invited to any arrival"}, status_code=400)

    if not student_data.submit_arrival:
        await delete_student_from_invitation_table(current_user.email, session)
        return JSONResponse(content={"detail": "User rejected invitation"}, status_code=200)

    await update_profile_by_invitation(student_data, arrival_data, current_user, session)

    await add_student_to_arrival(arrival_data.id, current_user.email, session)
    await delete_student_from_invitation_table(current_user.email, session)

    return JSONResponse(content={"detail": "User has been added to arrival"}, status_code=200)


@arrival_router.get("/arrivals",
                    status_code=status.HTTP_200_OK
                    )
async def get_all_arrivals(current_user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_async_session)):
    arrivals = await get_all_arrivals_dict(session)

    arrivals["past_arrivals"] = await format_arrivals_list(arrivals["past_arrivals"], session)
    arrivals["future_arrivals"] = await format_arrivals_list(arrivals["future_arrivals"], session)
    return arrivals


@arrival_router.get("/me/arrivals",
                    status_code=status.HTTP_200_OK
                    )
async def get_my_arrivals(current_user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_async_session)):
    arrivals = await get_buddy_arrivals(current_user.email, session)

    arrivals = await format_arrivals_list(arrivals, session)
    return arrivals


@arrival_router.get("/arrivals/{arrival_id}",
                    status_code=status.HTTP_200_OK
                    )
async def get_arrival_by_id(arrival_id: int, current_user: User = Depends(get_current_user),
                            session: AsyncSession = Depends(get_async_session)):
    arrival_data = await get_arrival_data_by_id(arrival_id, session)
    return arrival_data


@arrival_router.put("/arrivals/sign-up/{arrival_id}",
                    status_code=status.HTTP_200_OK
                    )
async def signup_to_arrival(arrival_id: int, current_user: User = Depends(get_current_user),
                            session: AsyncSession = Depends(get_async_session)):
    if not await check_active_arrival(current_user.id, session):
        return JSONResponse(content={"detail": "Buddy has active arrival"}, status_code=400)

    arrival_data = await get_arrival_data_by_id(arrival_id, session)
    students_count = len(arrival_data["students"])
    buddies_count = len(arrival_data["buddies"])
    required_buddies = 2 if students_count >= 3 else 1
    if buddies_count < required_buddies:
        if await add_buddy(current_user.id, arrival_id, session):
            student_ids = await get_students_ids(arrival_id, session)
            for student_id in student_ids:
                await create_chat(current_user.id, student_id, session)
                await add_student_to_table(current_user.id, arrival_id, student_id, session)
            await add_last_arrival_to_buddy(current_user.id, arrival_id, session)
            return JSONResponse(content={"detail": "Buddy has been added to arrival"}, status_code=200)
        return JSONResponse(content={"detail": "Buddy is already in this arrival"}, status_code=400)
    return JSONResponse(content={"detail": "Arrival already has max amount of buddies"}, status_code=400)


@teamleader_router.get("/buddies",
                       status_code=status.HTTP_200_OK
                       )
async def get_all_buddies(current_user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_async_session)):
    return await get_buddies(session)


@teamleader_router.put("/arrivals/add-buddy/",
                       status_code=status.HTTP_200_OK
                       )
async def add_buddy_to_arrival(data: AddBuddyToArrivalSchema, current_user: User = Depends(get_current_user),
                               session: AsyncSession = Depends(get_async_session)):
    if await add_buddy(data.buddy_id, data.arrival_id, session):
        student_ids = await get_students_ids(data.arrival_id, session)
        for student_id in student_ids:
            await create_chat(data.buddy_id, student_id, session)
            await add_student_to_table(data.buddy_id, data.arrival_id, student_id, session)
        await add_last_arrival_to_buddy(data.buddy_id, data.arrival_id, session)
        return JSONResponse(content={"detail": "Buddy has been added to arrival"}, status_code=200)
    return JSONResponse(content={"detail": "Buddy is already in this arrival"}, status_code=400)


@teamleader_router.put("/arrivals/confirm/{arrival_id}",
                       status_code=status.HTTP_200_OK
                       )
async def confirm_arrival_by_id(arrival_id: int, current_user: User = Depends(get_current_user),
                                session: AsyncSession = Depends(get_async_session)):
    await confirm_arrival(arrival_id, session)
    return JSONResponse(content={"detail": "Arrival has been confirmed"}, status_code=200)


@teamleader_router.delete("/arrivals/delete-buddy/",
                          status_code=status.HTTP_200_OK
                          )
async def delete_buddy_from_arrival(data: AddBuddyToArrivalSchema, current_user: User = Depends(get_current_user),
                                    session: AsyncSession = Depends(get_async_session)):
    if await delete_buddy(data.buddy_id, data.arrival_id, session):
        student_ids = await get_students_ids(data.arrival_id, session)
        for student_id in student_ids:
            await delete_chat(data.buddy_id, student_id, session)
            await delete_student_from_table(data.buddy_id, student_id, session)
        await delete_last_arrival_from_buddy(data.buddy_id, session)
        return JSONResponse(content={"detail": "Buddy has been deleted from arrival"}, status_code=200)
    return JSONResponse(content={"detail": "This buddy do not belong to this arrival"}, status_code=400)
