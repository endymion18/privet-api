from datetime import date, time
from typing import Optional

from pydantic import BaseModel, EmailStr


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
    invite: list[EmailStr]


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
