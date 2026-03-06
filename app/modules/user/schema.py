from pydantic import BaseModel, EmailStr
from typing import List

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserResponse]