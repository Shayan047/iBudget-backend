from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.dependencies import get_current_user
from .service import UserService
from .schema import UpdateName, ChangePassword, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch("/me", response_model=UserResponse)
def update_name(
    data: UpdateName,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserService.update_name(db, current_user, data)


@router.patch("/me/password")
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserService.change_password(db, current_user, data)
