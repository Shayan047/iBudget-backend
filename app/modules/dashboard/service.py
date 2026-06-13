from sqlalchemy.orm import Session
from sqlalchemy import extract, text
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

        # Budget for this month
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

        # Replace the personal_expenses + shared_entries queries with this single query
        recent_expenses_query = text("""
            SELECT 
                e.id,
                e.description,
                e.amount,
                e.amount AS my_amount,
                e.date,
                c.name AS category_name,
                FALSE AS is_shared
            FROM expenses e
            LEFT JOIN categories c ON c.id = e.category_id
            WHERE e.user_id = :user_id
            AND e.is_shared = FALSE
            AND EXTRACT(MONTH FROM e.date) = :month
            AND EXTRACT(YEAR FROM e.date) = :year

            UNION ALL

            SELECT 
                e.id,
                e.description,
                e.amount,
                seu.amount AS my_amount,
                e.date,
                c.name AS category_name,
                TRUE AS is_shared
            FROM shared_expense_users seu
            JOIN expenses e ON e.id = seu.expense_id
            LEFT JOIN categories c ON c.id = e.category_id
            WHERE seu.user_id = :user_id
            AND EXTRACT(MONTH FROM e.date) = :month
            AND EXTRACT(YEAR FROM e.date) = :year

            ORDER BY date DESC
            LIMIT 10
        """)

        rows = (
            db.execute(
                recent_expenses_query,
                {"user_id": current_user.id, "month": month, "year": year},
            )
            .mappings()
            .all()
        )

        expense_items = [dict(row) for row in rows]
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
