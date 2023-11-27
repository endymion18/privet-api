import datetime
import uuid
from typing import Optional

from pydantic import BaseModel

from src.profile.models import Buddy, Contacts, Student


class StudentProfile:
    user_id: uuid.UUID
    photo_filepath: str
    university: int
    full_name: str
    citizenship: int
    sex: str
    birthdate: datetime.date
    native_language: str
    escort_paid: bool

    def __init__(
            self,
            student_info: Student,
    ):
        self.user_id = student_info.user_id
        self.photo_filepath = student_info.photo_filepath
        self.university = student_info.university
        self.full_name = student_info.full_name
        self.citizenship = student_info.citizenship
        self.sex = student_info.sex
        self.birthdate = student_info.birthdate
        self.native_language = student_info.native_language
        self.escort_paid = student_info.escort_paid


class BuddyProfile:
    user_id: uuid.UUID
    photo_filepath: str
    university: int
    full_name: str
    city: str
    sex: str
    birthdate: datetime.date
    native_language: str
    buddy_status: bool

    def __init__(
            self,
            buddy_info: Buddy,
    ):
        self.user_id = buddy_info.user_id
        self.photo_filepath = buddy_info.photo_filepath
        self.university = buddy_info.university
        self.full_name = buddy_info.full_name
        self.city = buddy_info.city
        self.birthdate = buddy_info.birthdate
        self.native_language = buddy_info.native_language
        self.buddy_status = buddy_info.buddy_status


class ContactSchema:
    phone: str
    email: str
    telegram: str
    whatsapp: str
    vk: str

    def __init__(
            self,
            contacts_row: Contacts,
    ):
        self.phone = contacts_row.phone
        self.email = contacts_row.email
        self.telegram = contacts_row.telegram
        self.whatsapp = contacts_row.whatsapp
        self.vk = contacts_row.vk


class ChangeUserInfo(BaseModel):
    full_name: Optional[str]
    citizenship: Optional[int]
    city: Optional[str]
    sex: Optional[str]
    birthdate: Optional[datetime.date]
    phone: Optional[str]
    telegram: Optional[str]
    whatsapp: Optional[str]
    vk: Optional[str]
    native_language: Optional[int]
    other_languages_ids: list[int]
    university: Optional[int]
