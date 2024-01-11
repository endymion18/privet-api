from sqlalchemy import ForeignKey, Boolean, Identity, Integer
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from src.database import Base
from pydantic import BaseModel


class Task(Base):

    def as_dict(self):
        return [{c.name: getattr(self, c.name),
                 "deadline": None} for c in self.__table__.columns[2:]]

    __tablename__ = "profile_tasks"
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    arrival_id: Mapped[int] = mapped_column(ForeignKey("arrival.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    airport_meeting: Mapped[bool] = mapped_column(Boolean, default=False)
    motel_checked_in: Mapped[bool] = mapped_column(Boolean, default=False)
    money_exchange: Mapped[bool] = mapped_column(Boolean, default=False)
    sim_card_created: Mapped[bool] = mapped_column(Boolean, default=False)
    medical_examinated: Mapped[bool] = mapped_column(Boolean, default=False)
    passport_translated: Mapped[bool] = mapped_column(Boolean, default=False)
    bank_card: Mapped[bool] = mapped_column(Boolean, default=False)
    enrollment_documents: Mapped[bool] = mapped_column(Boolean, default=False)
    insurance: Mapped[bool] = mapped_column(Boolean, default=False)
    dormitory_documents: Mapped[bool] = mapped_column(Boolean, default=False)
    student_pass: Mapped[bool] = mapped_column(Boolean, default=False, server_default='False')
    student_ID: Mapped[bool] = mapped_column(Boolean, default=False)
    medical_tests: Mapped[bool] = mapped_column(Boolean, default=False)
    visa_extension: Mapped[bool] = mapped_column(Boolean, default=False)
    fingerprinting: Mapped[bool] = mapped_column(Boolean, default=False)


class TaskOperation(BaseModel):
    name: str
    value: bool


class SetTask(BaseModel):
    user_id: uuid.UUID
    tasks: list[TaskOperation] = []
