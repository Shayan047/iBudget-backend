from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Tax, Expense, Income, SharedExpenseUser, User
from sqlalchemy import text
from app.utils.pagination import PaginationMeta


class TaxService:

    @staticmethod
    def get_all_taxes(db: Session, current_user: User, page: int, limit: int):
        offset = (page - 1) * limit

        # Single query for all 3 tax types
        # Window function COUNT() OVER (PARTITION BY) counts shared users
        # per expense inside the query itself — no extra round trips
        query = text("""
            SELECT
                t.id,
                t.amount,
                t.expense_id,
                NULL::int AS income_id,
                FALSE AS is_derived,
                t.amount AS my_tax_amount,
                e.description
            FROM taxes t
            JOIN expenses e ON e.id = t.expense_id
            WHERE e.user_id = :user_id
            AND e.is_shared = FALSE

            UNION ALL

            SELECT
                t.id,
                t.amount,
                t.expense_id,
                NULL::int AS income_id,
                (NOT seu.is_creator) AS is_derived,
                -- window function: count users in this shared expense in one pass
                ROUND(
                    t.amount / COUNT(seu.id) OVER (PARTITION BY e.id)
                , 2) AS my_tax_amount,
                e.description
            FROM shared_expense_users seu
            JOIN expenses e ON e.id = seu.expense_id
            JOIN taxes t ON t.expense_id = e.id
            WHERE seu.user_id = :user_id

            UNION ALL

            SELECT
                t.id,
                t.amount,
                NULL::int AS expense_id,
                t.income_id,
                FALSE AS is_derived,
                t.amount AS my_tax_amount,
                i.description
            FROM taxes t
            JOIN incomes i ON i.id = t.income_id
            WHERE i.user_id = :user_id

            ORDER BY id ASC
            LIMIT :limit OFFSET :offset
        """)

        count_query = text("""
            SELECT COUNT(*) FROM (
                SELECT t.id FROM taxes t
                JOIN expenses e ON e.id = t.expense_id
                WHERE e.user_id = :user_id AND e.is_shared = FALSE

                UNION ALL

                SELECT t.id FROM shared_expense_users seu
                JOIN expenses e ON e.id = seu.expense_id
                JOIN taxes t ON t.expense_id = e.id
                WHERE seu.user_id = :user_id

                UNION ALL

                SELECT t.id FROM taxes t
                JOIN incomes i ON i.id = t.income_id
                WHERE i.user_id = :user_id
            ) AS total
        """)

        rows = (
            db.execute(
                query, {"user_id": current_user.id, "limit": limit, "offset": offset}
            )
            .mappings()
            .all()
        )

        total = db.execute(count_query, {"user_id": current_user.id}).scalar()

        return {
            "data": [dict(row) for row in rows],
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
    def get_tax_by_id(db: Session, tax_id: int, current_user: User) -> Tax:
        tax = db.query(Tax).filter(Tax.id == tax_id).first()
        if not tax:
            raise HTTPException(status_code=404, detail="Tax not found")

        if tax.expense_id:
            expense = db.query(Expense).filter(Expense.id == tax.expense_id).first()
            is_owner = expense and expense.user_id == current_user.id
            is_participant = (
                db.query(SharedExpenseUser)
                .filter(
                    SharedExpenseUser.expense_id == tax.expense_id,
                    SharedExpenseUser.user_id == current_user.id,
                )
                .first()
            )
            if not is_owner and not is_participant:
                raise HTTPException(status_code=403, detail="Not authorized")

        if tax.income_id:
            income = (
                db.query(Income)
                .filter(
                    Income.id == tax.income_id,
                    Income.user_id == current_user.id,
                )
                .first()
            )
            if not income:
                raise HTTPException(status_code=403, detail="Not authorized")

        return tax

    @staticmethod
    def delete_tax(db: Session, tax_id: int, current_user: User) -> None:
        tax = TaxService.get_tax_by_id(db, tax_id, current_user)
        db.delete(tax)
        db.commit()
