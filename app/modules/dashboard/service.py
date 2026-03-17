from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.models import Income, Expense, Budget, Category, User


class DashboardService:

    @staticmethod
    def get_dashboard(db: Session, current_user: User, month: int, year: int) -> dict:
        incomes = db.query(Income).filter(
            Income.user_id == current_user.id,
            extract("month", Income.date) == month,
            extract("year", Income.date) == year,
        ).all()
        total_income = sum(i.amount for i in incomes)

        expenses = db.query(Expense).filter(
            Expense.user_id == current_user.id,
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year,
        ).all()
        total_expenses = sum(e.amount for e in expenses)

        budget = db.query(Budget).filter(
            Budget.user_id == current_user.id,
            extract("month", Budget.date) == month,
            extract("year", Budget.date) == year,
        ).order_by(Budget.id.desc()).first()
        budget_amount = budget.amount if budget else 0.0

        expense_items = []
        for e in expenses:
            category = db.query(Category).filter(Category.id == e.category_id).first()
            expense_items.append({
                "id": e.id,
                "amount": e.amount,
                "date": e.date,
                "category_name": category.name if category else None,
            })

        return {
            "month": month,
            "year": year,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "budget": budget_amount,
            "remaining_balance": total_income - total_expenses,
            "expenses": expense_items,
        }