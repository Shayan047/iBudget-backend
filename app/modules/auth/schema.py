from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserRegister(UserBase):
    name: str


class UserLogin(UserBase):
    pass


class AuthResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        from_attributes = True


class RefreshRequest(BaseModel):
    refresh_token: str