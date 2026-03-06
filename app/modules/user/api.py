from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from .schema import UserRegister, UserResponse, UserLogin
from .service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    return UserService.register_user(db, user)


@router.post("/login", response_model=UserResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    return UserService.login_user(db, user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return UserService.get_user_by_id(db, user_id)


@router.get("/", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return UserService.get_all_users(db)