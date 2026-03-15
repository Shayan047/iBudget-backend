from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from .schema import UserLogin, UserRegister, RegisterResponse, RefreshRequest
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=RegisterResponse)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    return AuthService.register_user(db, user)


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    return AuthService.login_user(db, credentials)


@router.post("/refresh")
def refresh(body: RefreshRequest):
    return AuthService.refresh(body.refresh_token)