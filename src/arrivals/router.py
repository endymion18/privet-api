from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from src.arrivals.schemas import StudentArrivalData
from src.arrivals.utils import update_profile_by_arrival, submit_arrival, add_student_to_arrival
from src.auth.models import User
from src.auth.utils import get_current_user
from src.database import get_async_session

arrival_router = APIRouter(
    tags=["Arrivals"],
)


@arrival_router.post("/users/me/book-arrival",
                     status_code=status.HTTP_200_OK
                     )
async def book_new_arrival(arrival_data: list[StudentArrivalData], current_user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_async_session)):
    arrival_organizer = arrival_data[0]

    await update_profile_by_arrival(arrival_organizer, current_user, session)

    arrival_id = await submit_arrival(arrival_organizer, session)

    for student in arrival_data:
        await add_student_to_arrival(arrival_id, student.email, session)

    return JSONResponse(content={"detail": "Arrival has been booked"}, status_code=200)


@arrival_router.post("/arrivals",
                     status_code=status.HTTP_200_OK
                     )
async def get_all_arrivals(current_user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_async_session)):
    pass
