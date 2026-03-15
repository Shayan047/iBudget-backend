from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.models import Expense, User, Category
from .schema import ExpenseCreate, ExpenseUpdate


class ExpenseService:

    @staticmethod
    def create_expense(db: Session, expense_data: ExpenseCreate, current_user: User) -> Expense:
        category = db.query(Category).filter(Category.id == expense_data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        new_expense = Expense(
            user_id=current_user.id,
            category_id=expense_data.category_id,
            amount=expense_data.amount,
            **({"date": expense_data.date} if expense_data.date else {}),
        )

        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)

        return new_expense


    @staticmethod
    def get_all_expenses(db: Session, current_user: User) -> list[Expense]:
        return db.query(Expense).filter(Expense.user_id == current_user.id).all()
    
    @staticmethod
    def get_expense_by_id(db: Session, expense_id: int, current_user: User) -> Expense:
        expense = db.query(Expense).filter(
            Expense.id == expense_id,
            Expense.user_id == current_user.id
        ).first()

        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        return expense


    @staticmethod
    def update_expense(db: Session, expense_id: int, expense_data: ExpenseUpdate, current_user: User) -> Expense:
        expense = db.query(Expense).filter(
            Expense.id == expense_id,
            Expense.user_id == current_user.id
        ).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        if expense_data.category_id is not None:
            category = db.query(Category).filter(Category.id == expense_data.category_id).first()
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
            expense.category_id = expense_data.category_id

        if expense_data.amount is not None:
            expense.amount = expense_data.amount

        if expense_data.date is not None:
            expense.date = expense_data.date

        db.commit()
        db.refresh(expense)

        return expense


    @staticmethod
    def delete_expense(db: Session, expense_id: int, current_user: User) -> None:
        expense = db.query(Expense).filter(
            Expense.id == expense_id,
            Expense.user_id == current_user.id
        ).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        db.delete(expense)
        db.commit()

        return {"status": "Success", "message": "Expense deleted successfully"}