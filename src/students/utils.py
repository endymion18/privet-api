import uuid

from sqlalchemy import select, insert, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.profile.models import Student
from src.students.models import StudentsRelationship


async def add_student_to_table(buddy_id: uuid.UUID, arrival_id: int, student_id: uuid.UUID, session: AsyncSession):
    student_profile = await session.execute(select(Student).where(Student.user_id == student_id))
    student_profile = student_profile.scalar()

    await session.execute(insert(StudentsRelationship).values(
        buddy_id=buddy_id,
        arrival_id=arrival_id,
        student_id=student_id,
        student_photo=student_profile.photo_filepath,
        student_fullname=student_profile.full_name,
        student_citizenship=student_profile.citizenship
    ))

    await session.commit()


async def delete_student_from_table(buddy_id: uuid.UUID, student_id: uuid.UUID, session: AsyncSession):
    await session.execute(delete(StudentsRelationship).where(and_(StudentsRelationship.buddy_id == buddy_id,
                                                                  StudentsRelationship.student_id ==
                                                                  student_id)))
    await session.commit()
