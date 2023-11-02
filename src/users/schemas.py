from fastapi import Form
from pydantic import BaseModel


class UserRegister(BaseModel):
    email: str
    password: str

    role_id: int


class UserLogin:
    user_email: str
    password: str

    def __init__(
            self,
            user_email: str = Form(),
            password: str = Form(),
    ):
        self.user_email = user_email
        self.password = password
