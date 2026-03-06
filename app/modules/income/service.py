from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Income, User
from .schema import IncomeCreate, IncomeUpdate


class IncomeService:

    @staticmethod
    def create_income(db: Session, income_data: IncomeCreate) -> Income:
        user = db.query(User).filter(User.id == income_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_income = Income(
            user_id=income_data.user_id,
            amount=income_data.amount,
            **({"date": income_data.date} if income_data.date else {}),
        )

        db.add(new_income)
        db.commit()
        db.refresh(new_income)

        return new_income

    @staticmethod
    def get_income_by_id(db: Session, income_id: int) -> Income:
        income = db.query(Income).filter(Income.id == income_id).first()
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")

        return income

    @staticmethod
    def get_all_incomes(db: Session) -> list[Income]:
        return db.query(Income).all()

    @staticmethod
    def get_incomes_by_user(db: Session, user_id: int) -> list[Income]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return db.query(Income).filter(Income.user_id == user_id).all()

    @staticmethod
    def update_income(db: Session, income_id: int, income_data: IncomeUpdate) -> Income:
        income = db.query(Income).filter(Income.id == income_id).first()
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")

        if income_data.amount is not None:
            income.amount = income_data.amount

        if income_data.date is not None:
            income.date = income_data.date

        db.commit()
        db.refresh(income)

        return income

    @staticmethod
    def delete_income(db: Session, income_id: int) -> None:
        income = db.query(Income).filter(Income.id == income_id).first()
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")

        db.delete(income)
        db.commit()