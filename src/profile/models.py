from datetime import date
import uuid

from sqlalchemy import Identity, Integer, ForeignKey, String, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Student(Base):
    __tablename__ = "profile_student"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    photo_filepath: Mapped[str] = mapped_column(String(length=1000))
    full_name: Mapped[str] = mapped_column(String(length=320))
    citizenship: Mapped[int] = mapped_column(ForeignKey("country.id"))
    sex: Mapped[str] = mapped_column(String(length=6))
    birthdate: Mapped[date] = mapped_column(Date)
    native_language: Mapped[int] = mapped_column(ForeignKey("language.id"))
    university: Mapped[int] = mapped_column(ForeignKey("university.id"))
    escort_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    last_buddy: Mapped[int] = mapped_column(ForeignKey("profile_buddy.id"))
    institute: Mapped[int] = mapped_column(ForeignKey("institute.id"))
    study_program: Mapped[str] = mapped_column(String(length=100))
    arrival_date: Mapped[date] = mapped_column(Date)
    visa_expiration: Mapped[date] = mapped_column(Date)
    accommodation: Mapped[str] = mapped_column(String(length=200))
    comment: Mapped[str] = mapped_column(String(length=300))


class Buddy(Base):
    __tablename__ = "profile_buddy"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    photo_filepath: Mapped[str] = mapped_column(String(length=1000))
    full_name: Mapped[str] = mapped_column(String(length=320))
    city: Mapped[str] = mapped_column(String(length=100))
    birthdate: Mapped[date] = mapped_column(Date)
    native_language: Mapped[int] = mapped_column(ForeignKey("language.id"))
    buddy_status: Mapped[bool] = mapped_column(Boolean, default=False)


class Country(Base):
    __tablename__ = "country"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(length=60), nullable=False)
    icon_filepath: Mapped[str] = mapped_column(String(length=1000), nullable=True)


class Language(Base):
    __tablename__ = "language"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(length=60), nullable=False)
    people: Mapped[int] = mapped_column(Integer, nullable=False)


class Contacts(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    phone: Mapped[str] = mapped_column(String(length=12))
    email: Mapped[str] = mapped_column(String(length=320))
    telegram: Mapped[str] = mapped_column(String(length=100))
    whatsapp: Mapped[str] = mapped_column(String(length=12))
    vk: Mapped[str] = mapped_column(String(length=100))


class LanguagesRelationship(Base):
    __tablename__ = "user_languages"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    language: Mapped[int] = mapped_column(ForeignKey("language.id"))
