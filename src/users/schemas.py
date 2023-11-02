from pydantic import BaseModel


class UserRegister(BaseModel):
    email: str
    password: str

    role_id: int
