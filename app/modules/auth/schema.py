from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserRegister(UserBase):
    name: str


class UserLogin(UserBase):
    pass


class UserOut(BaseModel):
    id: int
    email: str
    name: str

    model_config = {"from_attributes": True}

class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RegisterResponse(BaseModel):
    user: UserOut
    auth: AuthTokens


class RefreshRequest(BaseModel):
    refresh_token: str