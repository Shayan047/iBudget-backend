from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import User
from .schema import UserLogin, UserRegister
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token


class AuthService:

    @staticmethod
    def login_user(db: Session, user_data: UserLogin) -> User:
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user:
            raise HTTPException(status_code=400, detail="Email not registered")
        
        if not verify_password(user_data.password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect password")

        return {
            "user": user,
            "auth": {
                "access_token": create_access_token(user.id),
                "refresh_token": create_refresh_token(user.id),
                "token_type": "bearer"
            }
        }


    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
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

        return {
            "user": new_user,
            "auth": {
                "access_token": create_access_token(new_user.id),
                "refresh_token": create_refresh_token(new_user.id),
                "token_type": "bearer"
            }
        }


    @staticmethod
    def refresh(token: str):
        from app.utils.jwt import decode_token
        user_id = decode_token(token)
        return {
            "access_token": create_access_token(user_id),
            "token_type": "bearer"
        }
    

    
    
    