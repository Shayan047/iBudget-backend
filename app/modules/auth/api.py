from fastapi import APIRouter, Depends, Cookie, Response
from sqlalchemy.orm import Session

from app.database import get_db
from .schema import UserLogin, UserRegister, AuthResponse
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    return AuthService.register_user(db, user)


@router.post("/login", response_model=AuthResponse)
def login(response: Response, credentials: UserLogin, db: Session = Depends(get_db)):
    return AuthService.login_user(db, credentials, response)


@router.post("/refresh")
def refresh(refresh_token: str = Cookie(None)):
    return AuthService.refresh(refresh_token)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return {"message": "Logged out successfully"}
