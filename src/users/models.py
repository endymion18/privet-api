from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID

from sqlalchemy import Integer, String, Boolean, ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(length=25), nullable=False)
