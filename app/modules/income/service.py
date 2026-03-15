from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Income, User
from .schema import IncomeCreate, IncomeUpdate


class IncomeService:

    @staticmethod
    def get_all_incomes(db: Session, current_user: User) -> list[Income]:
        return db.query(Income).filter(Income.user_id == current_user.id).all()

    @staticmethod
    def get_income_by_id(db: Session, income_id: int, current_user: User) -> Income:
        income = db.query(Income).filter(
            Income.id == income_id,
            Income.user_id == current_user.id
        ).first()
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")
        return income

    @staticmethod
    def create_income(db: Session, income_data: IncomeCreate, current_user: User) -> Income:
        income = Income(
            user_id=current_user.id,
            amount=income_data.amount,
            date=income_data.date
        )
        db.add(income)
        db.commit()
        db.refresh(income)
        return income

    @staticmethod
    def update_income(db: Session, income_id: int, income_data: IncomeUpdate, current_user: User) -> Income:
        income = db.query(Income).filter(
            Income.id == income_id,
            Income.user_id == current_user.id
        ).first()
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
    def delete_income(db: Session, income_id: int, current_user: User) -> None:
        income = db.query(Income).filter(
            Income.id == income_id,
            Income.user_id == current_user.id
        ).first()
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")

        db.delete(income)
        db.commit()

        return {"status": "Success", "message": "Income deleted successfully"}