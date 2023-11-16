from sqlalchemy import ForeignKey, Boolean, Identity, Integer
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from src.database import Base


class Task(Base):
    __tablename__ = "profile_tasks"
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
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
    student_ID: Mapped[bool] = mapped_column(Boolean, default=False)
    medical_tests: Mapped[bool] = mapped_column(Boolean, default=False)
    visa_extension: Mapped[bool] = mapped_column(Boolean, default=False)
    fingerprinting: Mapped[bool] = mapped_column(Boolean, default=False)

