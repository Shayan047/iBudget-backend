from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models import Income, Tax, User
from app.utils.pagination import PaginationMeta
from .schema import IncomeCreate, IncomeUpdate


class IncomeService:

    @staticmethod
    def get_all_incomes(db: Session, current_user: User, page: int, limit: int):
        offset = (page - 1) * limit

        total = db.query(Income).filter(Income.user_id == current_user.id).count()

        incomes = (
            db.query(Income)
            .filter(Income.user_id == current_user.id)
            .order_by(Income.date.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "data": incomes,
            "pagination": PaginationMeta(
                page=page,
                limit=limit,
                total=total,
                total_pages=-(-total // limit),
                has_next=offset + limit < total,
                has_prev=page > 1,
            ),
        }

    @staticmethod
    def get_income_by_id(db: Session, income_id: int, current_user: User) -> Income:
        income = (
            db.query(Income)
            .filter(
                Income.id == income_id,
                Income.user_id == current_user.id,
            )
            .first()
        )
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")
        return income

    @staticmethod
    def create_income(db: Session, data: IncomeCreate, current_user: User) -> Income:
        income = Income(
            user_id=current_user.id,
            amount=data.amount,
            description=data.description,
            date=data.date or datetime.utcnow(),
        )
        db.add(income)
        db.flush()

        if data.tax_amount is not None:
            db.add(Tax(amount=data.tax_amount, income_id=income.id))

        db.commit()
        db.refresh(income)
        return income

    @staticmethod
    def update_income(
        db: Session, income_id: int, data: IncomeUpdate, current_user: User
    ) -> Income:
        income = (
            db.query(Income)
            .filter(
                Income.id == income_id,
                Income.user_id == current_user.id,
            )
            .first()
        )
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")

        if data.amount is not None:
            income.amount = data.amount
        if data.description is not None:
            income.description = data.description
        if data.date is not None:
            income.date = data.date

        if data.tax_amount is not None:
            if data.tax_amount == 0:
                if income.tax:
                    db.delete(income.tax)
            else:
                if income.tax:
                    income.tax.amount = data.tax_amount
                else:
                    db.add(Tax(amount=data.tax_amount, income_id=income.id))

        db.commit()
        db.refresh(income)
        return income

    @staticmethod
    def delete_income(db: Session, income_id: int, current_user: User) -> dict:
        income = (
            db.query(Income)
            .filter(
                Income.id == income_id,
                Income.user_id == current_user.id,
            )
            .first()
        )
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")

        db.delete(income)
        db.commit()
        return {"status": "Success", "message": "Income deleted successfully"}
