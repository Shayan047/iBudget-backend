from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Budget, User
from .schema import BudgetCreate, BudgetUpdate


class BudgetService:

    @staticmethod
    def get_all_budgets(db: Session, current_user: User) -> list[Budget]:
        return db.query(Budget).filter(Budget.user_id == current_user.id).all()

    @staticmethod
    def get_budget_by_id(db: Session, budget_id: int, current_user: User) -> Budget:
        budget = (
            db.query(Budget)
            .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
            .first()
        )
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return budget

    @staticmethod
    def create_budget(
        db: Session, budget_data: BudgetCreate, current_user: User
    ) -> Budget:
        budget = Budget(
            user_id=current_user.id, amount=budget_data.amount, date=budget_data.date
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return budget

    @staticmethod
    def update_budget(
        db: Session, budget_id: int, budget_data: BudgetUpdate, current_user: User
    ) -> Budget:
        budget = (
            db.query(Budget)
            .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
            .first()
        )
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
    def delete_budget(db: Session, budget_id: int, current_user: User) -> None:
        budget = (
            db.query(Budget)
            .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
            .first()
        )
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        db.delete(budget)
        db.commit()

        return {"status": "Success", "message": "Budget deleted successfully"}
