from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.models import Expense, User, Category
from .schema import ExpenseCreate, ExpenseUpdate


class ExpenseService:

    @staticmethod
    def create_expense(db: Session, expense_data: ExpenseCreate) -> Expense:
        # Validate user exists
        user = db.query(User).filter(User.id == expense_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Validate category exists
        category = db.query(Category).filter(Category.id == expense_data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        new_expense = Expense(
            user_id=expense_data.user_id,
            category_id=expense_data.category_id,
            amount=expense_data.amount,
            **({"date": expense_data.date} if expense_data.date else {}),
        )

        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)

        return new_expense

    @staticmethod
    def get_expense_by_id(db: Session, expense_id: int) -> Expense:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        return expense

    @staticmethod
    def get_all_expenses(db: Session) -> list[Expense]:
        return db.query(Expense).all()

    @staticmethod
    def get_expenses_by_user(db: Session, user_id: int) -> list[Expense]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return db.query(Expense).options(joinedload(Expense.category)).filter(Expense.user_id == user_id).all()

    @staticmethod
    def update_expense(db: Session, expense_id: int, expense_data: ExpenseUpdate) -> Expense:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
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
    def delete_expense(db: Session, expense_id: int) -> None:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        db.delete(expense)
        db.commit()