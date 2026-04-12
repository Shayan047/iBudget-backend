from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Tax, Expense, Income, SharedExpenseUser, User
from .schema import TaxCreate


class TaxService:

    @staticmethod
    def create_tax(db: Session, data: TaxCreate, current_user: User) -> Tax:
        if data.expense_id and data.income_id:
            raise HTTPException(
                status_code=400,
                detail="Tax can only be linked to either an expense or an income, not both",
            )

        if data.expense_id:
            expense = (
                db.query(Expense)
                .filter(
                    Expense.id == data.expense_id,
                    Expense.user_id == current_user.id,
                )
                .first()
            )
            if not expense:
                raise HTTPException(status_code=404, detail="Expense not found")
            existing = db.query(Tax).filter(Tax.expense_id == data.expense_id).first()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="A tax already exists for this expense",
                )

        if data.income_id:
            income = (
                db.query(Income)
                .filter(
                    Income.id == data.income_id,
                    Income.user_id == current_user.id,
                )
                .first()
            )
            if not income:
                raise HTTPException(status_code=404, detail="Income not found")
            existing = db.query(Tax).filter(Tax.income_id == data.income_id).first()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="A tax already exists for this income",
                )

        tax = Tax(
            amount=data.amount,
            expense_id=data.expense_id,
            income_id=data.income_id,
        )
        db.add(tax)
        db.commit()
        db.refresh(tax)
        return tax

    @staticmethod
    def get_all_taxes(db: Session, current_user: User) -> list:
        results = []

        # 1. Taxes from user's own expenses (personal + shared they created)
        expense_taxes = (
            db.query(Tax)
            .join(Expense, Tax.expense_id == Expense.id)
            .filter(Expense.user_id == current_user.id)
            .all()
        )
        for tax in expense_taxes:
            results.append(
                {
                    "id": tax.id,
                    "amount": tax.amount,
                    "expense_id": tax.expense_id,
                    "income_id": tax.income_id,
                    "is_derived": False,  # real tax record
                    "my_tax_amount": tax.amount,
                }
            )

        # 2. Taxes from shared expenses where user is a participant (not creator)
        participant_entries = (
            db.query(SharedExpenseUser)
            .filter(
                SharedExpenseUser.user_id == current_user.id,
                SharedExpenseUser.is_creator == False,
            )
            .all()
        )
        for entry in participant_entries:
            expense = entry.expense
            if expense and expense.tax:
                tax = expense.tax
                # Calculate proportional tax
                my_tax = round((entry.amount / expense.amount) * tax.amount, 2)
                results.append(
                    {
                        "id": tax.id,
                        "amount": tax.amount,  # total tax on the expense
                        "expense_id": expense.id,
                        "income_id": None,
                        "is_derived": True,  # calculated, not owned
                        "my_tax_amount": my_tax,  # participant's share of tax
                    }
                )

        # 3. Taxes from user's incomes
        income_taxes = (
            db.query(Tax)
            .join(Income, Tax.income_id == Income.id)
            .filter(Income.user_id == current_user.id)
            .all()
        )
        for tax in income_taxes:
            results.append(
                {
                    "id": tax.id,
                    "amount": tax.amount,
                    "expense_id": tax.expense_id,
                    "income_id": tax.income_id,
                    "is_derived": False,
                    "my_tax_amount": tax.amount,
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
            # Allow access if user is owner OR a participant
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
