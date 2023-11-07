from sqlalchemy import Integer, String, Identity
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class University(Base):
    __tablename__ = "university"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(length=40), nullable=False)
