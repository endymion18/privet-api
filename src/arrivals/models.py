from datetime import datetime

from sqlalchemy import Identity, Integer, DateTime, ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Arrival(Base):
    __tablename__ = 'arrival'

    id: Mapped[int] = mapped_column(Integer, Identity(start=100), primary_key=True)
    arrival_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    flight_number: Mapped[str] = mapped_column(String(length=20), nullable=False)
    arrival_point: Mapped[str] = mapped_column(String(length=20), nullable=False)
    comment: Mapped[str] = mapped_column(String(length=300), nullable=True)
    tickets: Mapped[str] = mapped_column(String(length=1000), nullable=True)

    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)


class ArrivalParticipants(Base):
    __tablename__ = 'arrival_participants'

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    arrival_id: Mapped[int] = mapped_column(ForeignKey("arrival.id"))
    participant_email: Mapped[str] = mapped_column(ForeignKey("user.email"))
    participant_role: Mapped[int] = mapped_column(ForeignKey("role.id"))


class ArrivalInvitations(Base):
    __tablename__ = 'arrival_invitations'

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    arrival_id: Mapped[int] = mapped_column(ForeignKey("arrival.id"))
    student_email: Mapped[str] = mapped_column(ForeignKey("user.email"))
