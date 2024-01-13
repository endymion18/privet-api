import uuid

from sqlalchemy import Identity, Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class StudentsRelationship(Base):
    __tablename__ = 'students_relationship'

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    buddy_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    arrival_id: Mapped[int] = mapped_column(ForeignKey("arrival.id"))
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    student_photo: Mapped[str] = mapped_column(String(length=1000), nullable=True)
    student_fullname: Mapped[str] = mapped_column(String(length=320), nullable=True)
    student_citizenship: Mapped[int] = mapped_column(ForeignKey("country.id"), nullable=True)
