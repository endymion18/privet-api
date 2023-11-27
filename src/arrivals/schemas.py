from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StudentArrivalData(BaseModel):
    full_name: str
    sex: str
    arrival_date: datetime
    flight_number: str
    arrival_point: str
    citizenship: int
    phone: Optional[str]
    telegram: Optional[str]
    whatsapp: Optional[str]
    vk: Optional[str]
    comment: Optional[str]
    tickets: Optional[str]


class Arrival(BaseModel):
    students: list[StudentArrivalData]
    arrival_date: datetime
