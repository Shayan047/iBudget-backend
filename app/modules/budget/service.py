from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Budget, User
from .schema import BudgetCreate, BudgetUpdate


class BudgetService:

    @staticmethod
    def create_budget(db: Session, budget_data: BudgetCreate) -> Budget:
        user = db.query(User).filter(User.id == budget_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_budget = Budget(
            user_id=budget_data.user_id,
            amount=budget_data.amount,
            **({"date": budget_data.date} if budget_data.date else {}),
        )

        db.add(new_budget)
        db.commit()
        db.refresh(new_budget)

        return new_budget

    @staticmethod
    def get_budget_by_id(db: Session, budget_id: int) -> Budget:
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        return budget

    @staticmethod
    def get_all_budgets(db: Session) -> list[Budget]:
        return db.query(Budget).all()

    @staticmethod
    def get_budgets_by_user(db: Session, user_id: int) -> list[Budget]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return db.query(Budget).filter(Budget.user_id == user_id).all()

    @staticmethod
    def update_budget(db: Session, budget_id: int, budget_data: BudgetUpdate) -> Budget:
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        if budget_data.amount is not None:
            budget.amount = budget_data.amount

        if budget_data.date is not None:
            budget.date = budget_data.date

        db.commit()
        db.refresh(budget)

        return budget

    @staticmethod
    def delete_budget(db: Session, budget_id: int) -> None:
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        db.delete(budget)
        db.commit()