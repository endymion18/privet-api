from pydantic import BaseModel


class UserRegister(BaseModel):
    email: str
    password: str

    role_id: int


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class VerifyEmail(BaseModel):
    email: str
    token: str
