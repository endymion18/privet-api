from datetime import date, time
from typing import Optional

from pydantic import BaseModel


class StudentArrivalData(BaseModel):
    email: str
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
