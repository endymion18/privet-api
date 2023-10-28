from uuid import UUID

from pydantic import BaseModel


class UserRegister(BaseModel):
    email: str
    password: str

    role_id: int
