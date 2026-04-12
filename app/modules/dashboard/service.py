from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.models import Income, Expense, Budget, Category, SharedExpenseUser, User


class DashboardService:

    @staticmethod
    def get_dashboard(db: Session, current_user: User, month: int, year: int) -> dict:
        # Total income
        incomes = (
            db.query(Income)
            .filter(
                Income.user_id == current_user.id,
                extract("month", Income.date) == month,
                extract("year", Income.date) == year,
            )
            .all()
        )
        total_income = sum(i.amount for i in incomes)

        # Budget
        budget = (
            db.query(Budget)
            .filter(
                Budget.user_id == current_user.id,
                extract("month", Budget.date) == month,
                extract("year", Budget.date) == year,
            )
            .order_by(Budget.id.desc())
            .first()
        )
        budget_amount = budget.amount if budget else 0.0

        # Personal expenses for this month
        personal_expenses = (
            db.query(Expense)
            .filter(
                Expense.user_id == current_user.id,
                Expense.is_shared == False,
                extract("month", Expense.date) == month,
                extract("year", Expense.date) == year,
            )
            .all()
        )

        # Shared expense entries for this month (creator + participant)
        shared_entries = (
            db.query(SharedExpenseUser)
            .filter(
                SharedExpenseUser.user_id == current_user.id,
                extract("month", Expense.date) == month,
                extract("year", Expense.date) == year,
            )
            .join(Expense, SharedExpenseUser.expense_id == Expense.id)
            .all()
        )

        # Build expense list
        expense_items = []

        for exp in personal_expenses:
            expense_items.append(
                {
                    "id": exp.id,
                    "amount": exp.amount,
                    "my_amount": exp.amount,
                    "date": exp.date,
                    "category_name": exp.category.name if exp.category else None,
                    "is_shared": False,
                }
            )

        for entry in shared_entries:
            exp = entry.expense
            expense_items.append(
                {
                    "id": exp.id,
                    "description": exp.description,
                    "amount": exp.amount,
                    "my_amount": entry.amount,
                    "date": exp.date,
                    "category_name": exp.category.name if exp.category else None,
                    "is_shared": True,
                }
            )

        total_expenses = sum(e["my_amount"] for e in expense_items)

        return {
            "month": month,
            "year": year,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "budget": budget_amount,
            "remaining_balance": total_income - total_expenses,
            "expenses": expense_items,
        }
