from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import User
from app.utils.hashing import hash_password, verify_password

class UserService:

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    @staticmethod
    def get_all_users(db: Session):
        return db.query(User).all()