from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.utils.jwt import decode_token

security = HTTPBearer()


def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)) -> User:
    try:
        print('test')
        print(f"Decoded user ID from token: {decode_token(token)}")  # Debugging statement
        user_id = decode_token(token)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )