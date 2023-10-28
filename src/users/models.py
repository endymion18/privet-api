import uuid

from sqlalchemy import Integer, String, ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column

from fastapi_users_db_sqlalchemy.generics import GUID

from src.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(length=25), nullable=False)
