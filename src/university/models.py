from sqlalchemy import Integer, String, Identity, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class University(Base):
    __tablename__ = "university"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(length=40), nullable=False)


class Institute(Base):
    __tablename__ = "institute"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("university.id"))
    name: Mapped[str] = mapped_column(String(length=40), nullable=False)
    people_count: Mapped[int] = mapped_column(Integer, default=0)
