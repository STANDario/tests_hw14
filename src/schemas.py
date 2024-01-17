from datetime import date
from pydantic import BaseModel, EmailStr, Field


class ContactModel(BaseModel):
    first_name: str
    surname: str
    email: EmailStr
    phone_number: str
    birthday: date


class ContactResponse(ContactModel):
    id: int = 1

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(min_length=5, max_length=20)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar: str

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class RequestPassword(BaseModel):
    password: str = Field(min_length=5, max_length=20)
