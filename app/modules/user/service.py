from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import User
from .schema import UserRegister, UserLogin
from app.utils.hashing import hash_password, verify_password

class UserService:

    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = User(
            email=user_data.email,
            password=hash_password(user_data.password),
            name=user_data.name,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    
    @staticmethod
    def login_user(db: Session, user_data: UserLogin) -> User:
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user:
            raise HTTPException(status_code=400, detail="Email not registered")
        
        if not verify_password(user_data.password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect password")

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    @staticmethod
    def get_all_users(db: Session):
        return db.query(User).all()