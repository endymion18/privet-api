from sqlalchemy import Identity, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from src.database import Base
from datetime import datetime


class Chat(Base):

    __tablename__ = "chat"
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    first_user: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    second_user: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))


class Message(Base):
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    from_user: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    date_print: Mapped[datetime] = mapped_column(DateTime)
    text: Mapped[str] = mapped_column(String, nullable=False)
    attachment: Mapped[str] = mapped_column(String)