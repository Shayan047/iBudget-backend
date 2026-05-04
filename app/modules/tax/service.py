from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Tax, Expense, Income, SharedExpenseUser, User


class TaxService:

    @staticmethod
    def get_all_taxes(db: Session, current_user: User) -> list:
        results = []

        expense_taxes = (
            db.query(Tax)
            .join(Expense, Tax.expense_id == Expense.id)
            .filter(
                Expense.user_id == current_user.id,
                Expense.is_shared == False,
            )
            .all()
        )
        for tax in expense_taxes:
            expense = db.query(Expense).filter(Expense.id == tax.expense_id).first()
            results.append(
                {
                    "id": tax.id,
                    "amount": tax.amount,
                    "expense_id": tax.expense_id,
                    "income_id": None,
                    "is_derived": False,
                    "my_tax_amount": tax.amount,
                    "description": expense.description if expense else None,
                }
            )

        shared_entries = (
            db.query(SharedExpenseUser)
            .filter(SharedExpenseUser.user_id == current_user.id)
            .all()
        )
        for entry in shared_entries:
            expense = entry.expense
            if expense and expense.tax:
                tax = expense.tax
                total_users = (
                    db.query(SharedExpenseUser)
                    .filter(SharedExpenseUser.expense_id == expense.id)
                    .count()
                )
                my_tax = round(tax.amount / total_users, 2) if total_users > 0 else 0
                results.append(
                    {
                        "id": tax.id,
                        "amount": tax.amount,
                        "expense_id": expense.id,
                        "income_id": None,
                        "is_derived": not entry.is_creator,
                        "my_tax_amount": my_tax,
                        "description": expense.description,
                    }
                )

        income_taxes = (
            db.query(Tax)
            .join(Income, Tax.income_id == Income.id)
            .filter(Income.user_id == current_user.id)
            .all()
        )
        for tax in income_taxes:
            income = db.query(Income).filter(Income.id == tax.income_id).first()
            results.append(
                {
                    "id": tax.id,
                    "amount": tax.amount,
                    "expense_id": None,
                    "income_id": tax.income_id,
                    "is_derived": False,
                    "my_tax_amount": tax.amount,
                    "description": income.description if income else None,
                }
            )

        return results

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
