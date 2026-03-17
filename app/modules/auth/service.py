from sqlalchemy.orm import Session
from fastapi import HTTPException, Response

from app.models import User
from .schema import UserLogin, UserRegister
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token


class AuthService:

    @staticmethod
    def login_user(db: Session, user_data: UserLogin, response: Response) -> User:
        user = db.query(User).filter(User.email == user_data.email).first()

        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        response.set_cookie(
            key="refresh_token",
            value=create_refresh_token(user.id),
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
        )

        return {
            "user": user,
            "auth": {
                "access_token": create_access_token(user.id),
                "token_type": "bearer",
            },
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
        }

    @staticmethod
    def refresh(refresh_token: str):
        from app.utils.jwt import decode_token

        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token provided")

        print("Received refresh token:", refresh_token)
        user_id = decode_token(refresh_token)

        if not user_id:
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )

        return {"access_token": create_access_token(user_id), "token_type": "bearer"}
