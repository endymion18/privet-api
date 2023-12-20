import uuid
from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from src.arrivals.models import Arrival


class StudentArrivalData(BaseModel):
    full_name: str
    sex: str
    arrival_date: date
    arrival_time: time
    flight_number: str
    arrival_point: str
    citizenship: int
    phone: Optional[str]
    telegram: Optional[str]
    whatsapp: Optional[str]
    vk: Optional[str]
    comment: Optional[str]
    tickets: Optional[str]


class ArrivalData(BaseModel):
    student_data: StudentArrivalData
    invite: Optional[list[EmailStr]]


class InvitedStudentData(BaseModel):
    full_name: str
    sex: str
    citizenship: int
    phone: Optional[str]
    telegram: Optional[str]
    whatsapp: Optional[str]
    vk: Optional[str]
    tickets: Optional[str]
    submit_arrival: bool


class FormattedArrival:
    arrival_id: int
    arrival_date: datetime
    group_full_names: list[str]
    group_countries: list[int]
    buddies_amount: str

    def __init__(self, arrival_data: Arrival,
                 group_full_names: list[str],
                 group_countries: list[int],
                 buddies_amount: str):
        self.arrival_id = arrival_data.id
        self.arrival_date = arrival_data.arrival_date

        group_full_names = group_full_names[0:3] if len(group_full_names) >= 3 else group_full_names
        group_countries = group_countries[0:3] if len(group_countries) >= 3 else group_countries

        self.group_full_names = group_full_names
        self.group_countries = group_countries
        self.buddies_amount = buddies_amount


class StudentArrivalDataSchema:
    full_name: str
    sex: str
    arrival_date: date
    arrival_time: time
    flight_number: str
    arrival_point: str
    citizenship: int
    phone: Optional[str]
    telegram: Optional[str]
    whatsapp: Optional[str]
    vk: Optional[str]
    comment: Optional[str]
    tickets: Optional[str]

    def __init__(self, student_data, arrival_data):
        self.full_name = student_data["profile_info"].full_name
        self.sex = student_data["profile_info"].sex
        self.arrival_date = arrival_data.arrival_date.date()
        self.arrival_time = arrival_data.arrival_date.timetz()
        self.flight_number = arrival_data.flight_number
        self.arrival_point = arrival_data.arrival_point
        self.citizenship = student_data["profile_info"].citizenship
        self.phone = student_data["contacts"].phone
        self.telegram = student_data["contacts"].telegram
        self.vk = student_data["contacts"].vk
        self.comment = arrival_data.comment
        self.tickets = None


class BuddyArrivalSchema:
    full_name: str
    photo: Optional[str]

    def __init__(self, buddy_data):
        self.full_name = buddy_data["profile_info"].full_name
        self.photo = buddy_data["profile_info"].photo_filepath


class BuddySchema:
    id: uuid.UUID
    full_name: str

    def __init__(self, buddy_data):
        self.id = buddy_data.user_id
        self.full_name = buddy_data.full_name


class AddBuddyToArrivalSchema(BaseModel):
    buddy_id: uuid.UUID
    arrival_id: int
