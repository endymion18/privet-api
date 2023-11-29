from datetime import date
import uuid

from sqlalchemy import Identity, Integer, ForeignKey, String, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Student(Base):
    __tablename__ = "profile_student"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    photo_filepath: Mapped[str] = mapped_column(String(length=1000), nullable=True)
    full_name: Mapped[str] = mapped_column(String(length=320), nullable=True)
    citizenship: Mapped[int] = mapped_column(ForeignKey("country.id"), nullable=True)
    sex: Mapped[str] = mapped_column(String(length=6), nullable=True)
    birthdate: Mapped[date] = mapped_column(Date, nullable=True)
    native_language: Mapped[int] = mapped_column(ForeignKey("language.id"), nullable=True)
    university: Mapped[int] = mapped_column(ForeignKey("university.id"), nullable=True)
    escort_paid: Mapped[bool] = mapped_column(Boolean, default=True)
    last_buddy: Mapped[int] = mapped_column(ForeignKey("profile_buddy.id"), nullable=True)
    institute: Mapped[int] = mapped_column(ForeignKey("institute.id"), nullable=True)
    study_program: Mapped[str] = mapped_column(String(length=100), nullable=True)
    arrival_date: Mapped[date] = mapped_column(Date, nullable=True)
    visa_expiration: Mapped[date] = mapped_column(Date, nullable=True)
    accommodation: Mapped[str] = mapped_column(String(length=200), nullable=True)
    comment: Mapped[str] = mapped_column(String(length=300), nullable=True)


class Buddy(Base):
    __tablename__ = "profile_buddy"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    photo_filepath: Mapped[str] = mapped_column(String(length=1000), nullable=True)
    university: Mapped[int] = mapped_column(ForeignKey("university.id"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(length=320), nullable=True)
    city: Mapped[str] = mapped_column(String(length=100), nullable=True)
    sex: Mapped[str] = mapped_column(String(length=6), nullable=True)
    birthdate: Mapped[date] = mapped_column(Date, nullable=True)
    native_language: Mapped[int] = mapped_column(ForeignKey("language.id"), nullable=True)
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
    phone: Mapped[str] = mapped_column(String(length=12), nullable=True)
    email: Mapped[str] = mapped_column(String(length=320))
    telegram: Mapped[str] = mapped_column(String(length=100), nullable=True)
    whatsapp: Mapped[str] = mapped_column(String(length=12), nullable=True)
    vk: Mapped[str] = mapped_column(String(length=100), nullable=True)


class LanguagesRelationship(Base):
    __tablename__ = "user_languages"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    language: Mapped[int] = mapped_column(ForeignKey("language.id"))
