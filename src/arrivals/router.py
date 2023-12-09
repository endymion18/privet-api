from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from src.arrivals.schemas import ArrivalData, InvitedStudentData
from src.arrivals.utils import update_profile_by_arrival, submit_arrival, add_student_to_invites, \
    add_student_to_arrival, check_invitation_in_db, update_profile_by_invitation, delete_student_from_invitation_table, \
    check_current_arrival
from src.auth.models import User
from src.auth.utils import get_current_user
from src.database import get_async_session
from src.profile.router import get_user_profile_info

arrival_router = APIRouter(
    tags=["Arrivals"],
)


@arrival_router.get("/check-payment/{email}",
                    status_code=status.HTTP_200_OK
                    )
async def check_payment(email: str,
                        session: AsyncSession = Depends(get_async_session)):
    user_profile = await get_user_profile_info(email, session)

    if isinstance(user_profile, JSONResponse):
        return user_profile

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


@arrival_router.post("/arrivals",
                     status_code=status.HTTP_200_OK
                     )
async def get_all_arrivals(current_user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_async_session)):
    pass
