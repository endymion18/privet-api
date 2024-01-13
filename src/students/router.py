from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from src.auth.models import User
from src.auth.utils import get_current_user
from src.database import get_async_session
from src.profile.router import get_user_avatar_by_id
from src.students.models import StudentsRelationship

students_router = APIRouter(
    tags=["Students"],
)


@students_router.get("/me/my-students",
                     status_code=status.HTTP_200_OK
                     )
async def get_my_students(current_user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_async_session)):
    if current_user.role_id not in (2, 3):
        return JSONResponse(content={"detail": "You are not buddy"}, status_code=400)
    students = await session.execute(
        select(StudentsRelationship).where(StudentsRelationship.buddy_id == current_user.id))
    students = students.scalars().all()

    students_result = []
    for student in students:
        student_photo = await get_user_avatar_by_id(student.student_id, session)
        students_result.append({
            "arrival_id": student.arrival_id,
            "student_id": student.student_id,
            "student_photo": student_photo,
            "student_fullname": student.student_fullname,
            "student_citizenship": student.student_citizenship,
        })

    return students_result
