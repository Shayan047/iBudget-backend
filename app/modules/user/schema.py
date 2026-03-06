from pydantic import BaseModel, EmailStr
from typing import List


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserRegister(UserBase):
    name: str


class UserLogin(UserBase):
    pass


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserResponse]