from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import User
from app.utils.hashing import hash_password, verify_password
from .schema import UpdateName, ChangePassword


class UserService:

    @staticmethod
    def update_name(db: Session, current_user: User, data: UpdateName) -> User:
        current_user.name = data.name
        db.commit()
        db.refresh(current_user)
        return current_user

    @staticmethod
    def change_password(db: Session, current_user: User, data: ChangePassword) -> dict:
        if not verify_password(data.current_password, current_user.password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        current_user.password = hash_password(data.new_password)
        db.commit()
        return {"message": "Password updated successfully"}
