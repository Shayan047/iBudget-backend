from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models import (
    Expense,
    SharedExpenseUser,
    SharedExpenseStatus,
    Category,
    Tax,
    User,
)
from .schema import (
    ExpenseCreate,
    ExpenseUpdate,
    SharedExpenseCreate,
    SharedExpenseUpdate,
)


class ExpenseService:

    @staticmethod
    def get_all_expenses(db: Session, current_user: User) -> list:
        results = []

        personal = (
            db.query(Expense)
            .filter(
                Expense.user_id == current_user.id,
                Expense.is_shared == False,
            )
            .all()
        )
        for exp in personal:
            results.append({
                "id": exp.id,
                "description": exp.description,
                "my_amount": exp.amount,
                "date": exp.date,
                "category": exp.category,
                "is_shared": False,
                "is_creator": None,
                "status": None,
            })

        shared_entries = (
            db.query(SharedExpenseUser)
            .filter(SharedExpenseUser.user_id == current_user.id)
            .all()
        )
        for entry in shared_entries:
            exp = entry.expense
            results.append({
                "id": exp.id,
                "description": exp.description,
                "my_amount": entry.amount,
                "date": exp.date,
                "category": exp.category,
                "is_shared": True,
                "is_creator": entry.is_creator,
                "status": entry.status,
            })

        return results

    @staticmethod
    def get_expense_by_id(db: Session, expense_id: int, current_user: User) -> dict:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        if expense.is_shared:
            entry = (
                db.query(SharedExpenseUser)
                .filter(
                    SharedExpenseUser.expense_id == expense_id,
                    SharedExpenseUser.user_id == current_user.id,
                )
                .first()
            )
            if not entry:
                raise HTTPException(status_code=403, detail="Not authorized")
            return ExpenseService._format_shared_detail(db, expense)
        else:
            if expense.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
            return ExpenseService._format_personal_detail(expense)

    @staticmethod
    def create_expense(db: Session, data: ExpenseCreate, current_user: User) -> dict:
        category = db.query(Category).filter(Category.id == data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        expense = Expense(
            user_id=current_user.id,
            category_id=data.category_id,
            amount=data.amount,
            description=data.description,
            date=data.date or datetime.utcnow(),
            is_shared=False,
        )
        db.add(expense)
        db.flush()

        # Create tax if provided
        if data.tax_amount is not None:
            tax = Tax(amount=data.tax_amount, expense_id=expense.id)
            db.add(tax)

        db.commit()
        db.refresh(expense)
        return ExpenseService._format_personal_detail(expense)

    @staticmethod
    def create_shared_expense(
        db: Session, data: SharedExpenseCreate, current_user: User
    ) -> dict:
        participants = []
        for entry in data.users:
            user = db.query(User).filter(User.email == entry.email).first()
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail=f"User with email '{entry.email}' not found",
                )
            participants.append((user, entry.amount))

        total_shares = round(data.my_share + sum(u.amount for u in data.users), 2)
        if total_shares != round(data.total_amount, 2):
            raise HTTPException(
                status_code=400,
                detail=f"Shares ({total_shares}) do not match total amount ({data.total_amount})",
            )

        category = db.query(Category).filter(Category.id == data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        expense = Expense(
            user_id=current_user.id,
            category_id=data.category_id,
            amount=data.total_amount,
            description=data.description,
            date=data.date or datetime.utcnow(),
            is_shared=True,
        )
        db.add(expense)
        db.flush()

        db.add(SharedExpenseUser(
            expense_id=expense.id,
            user_id=current_user.id,
            amount=data.my_share,
            status=SharedExpenseStatus.paid,
            is_creator=True,
        ))

        for user, amount in participants:
            db.add(SharedExpenseUser(
                expense_id=expense.id,
                user_id=user.id,
                amount=amount,
                status=SharedExpenseStatus.pending,
                is_creator=False,
            ))

        # Create tax if provided
        if data.tax_amount is not None:
            tax = Tax(amount=data.tax_amount, expense_id=expense.id)
            db.add(tax)

        db.commit()
        db.refresh(expense)
        return ExpenseService._format_shared_detail(db, expense)

    @staticmethod
    def update_expense(
        db: Session, expense_id: int, data: ExpenseUpdate, current_user: User
    ) -> dict:
        expense = (
            db.query(Expense)
            .filter(
                Expense.id == expense_id,
                Expense.user_id == current_user.id,
                Expense.is_shared == False,
            )
            .first()
        )
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        if data.category_id is not None:
            category = db.query(Category).filter(Category.id == data.category_id).first()
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
            expense.category_id = data.category_id
        if data.amount is not None:
            expense.amount = data.amount
        if data.description is not None:
            expense.description = data.description
        if data.date is not None:
            expense.date = data.date

        # Handle tax update
        if data.tax_amount is not None:
            if expense.tax:
                # Update existing tax
                expense.tax.amount = data.tax_amount
            else:
                # Create new tax
                db.add(Tax(amount=data.tax_amount, expense_id=expense.id))
        elif data.tax_amount == 0 and expense.tax:
            # tax_amount of 0 means remove the tax
            db.delete(expense.tax)

        db.commit()
        db.refresh(expense)
        return ExpenseService._format_personal_detail(expense)

    @staticmethod
    def update_shared_expense(
        db: Session, expense_id: int, data: SharedExpenseUpdate, current_user: User
    ) -> dict:
        expense = (
            db.query(Expense)
            .filter(
                Expense.id == expense_id,
                Expense.user_id == current_user.id,
                Expense.is_shared == True,
            )
            .first()
        )
        if not expense:
            raise HTTPException(
                status_code=404,
                detail="Shared expense not found or you are not the creator",
            )

        new_participants = []
        if data.users is not None:
            for entry in data.users:
                user = db.query(User).filter(User.email == entry.email).first()
                if not user:
                    raise HTTPException(
                        status_code=404,
                        detail=f"User with email '{entry.email}' not found",
                    )
                new_participants.append((user, entry.amount, entry.status))

            total_amount = data.total_amount or expense.amount
            my_share = data.my_share
            if my_share is None:
                creator_entry = (
                    db.query(SharedExpenseUser)
                    .filter(
                        SharedExpenseUser.expense_id == expense_id,
                        SharedExpenseUser.is_creator == True,
                    )
                    .first()
                )
                my_share = creator_entry.amount if creator_entry else 0

            total_shares = round(my_share + sum(u.amount for u in data.users), 2)
            if total_shares != round(total_amount, 2):
                raise HTTPException(
                    status_code=400,
                    detail=f"Shares ({total_shares}) do not match total amount ({total_amount})",
                )

        if data.category_id is not None:
            category = db.query(Category).filter(Category.id == data.category_id).first()
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
            expense.category_id = data.category_id
        if data.total_amount is not None:
            expense.amount = data.total_amount
        if data.description is not None:
            expense.description = data.description
        if data.date is not None:
            expense.date = data.date

        # Handle tax update
        if data.tax_amount is not None:
            if expense.tax:
                expense.tax.amount = data.tax_amount
            else:
                db.add(Tax(amount=data.tax_amount, expense_id=expense.id))
        elif data.tax_amount == 0 and expense.tax:
            db.delete(expense.tax)

        db.flush()

        if data.users is not None:
            db.query(SharedExpenseUser).filter(
                SharedExpenseUser.expense_id == expense_id
            ).delete()
            db.flush()

            db.add(SharedExpenseUser(
                expense_id=expense.id,
                user_id=current_user.id,
                amount=data.my_share,
                status=SharedExpenseStatus.paid,
                is_creator=True,
            ))

            for user, amount, status in new_participants:
                db.add(SharedExpenseUser(
                    expense_id=expense.id,
                    user_id=user.id,
                    amount=amount,
                    status=status,
                    is_creator=False,
                ))

        db.commit()
        db.refresh(expense)
        return ExpenseService._format_shared_detail(db, expense)

    @staticmethod
    def delete_expense(db: Session, expense_id: int, current_user: User) -> dict:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        if expense.is_shared and expense.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete this shared expense",
            )

        db.delete(expense)
        db.commit()
        return {"status": "Success", "message": "Expense deleted successfully"}

    @staticmethod
    def _format_personal_detail(expense: Expense) -> dict:
        return {
            "id": expense.id,
            "description": expense.description,
            "date": expense.date,
            "category": expense.category,
            "is_shared": False,
            "tax": expense.tax,
            "amount": expense.amount,
            "total_amount": None,
            "participants": None,
        }

    @staticmethod
    def _format_shared_detail(db: Session, expense: Expense) -> dict:
        participants = (
            db.query(SharedExpenseUser)
            .filter(SharedExpenseUser.expense_id == expense.id)
            .all()
        )
        tax_amount = expense.tax.amount if expense.tax else None
        total_users = len(participants)  # includes creator

        participant_list = []
        for p in participants:
            user = db.query(User).filter(User.id == p.user_id).first()

            # Equal split: tax / total number of users (not proportional)
            participant_tax = (
                round(tax_amount / total_users, 2)
                if tax_amount and total_users > 0
                else None
            )

            participant_list.append({
                "id": p.id,
                "user_id": p.user_id,
                "user_name": user.name if user else None,
                "user_email": user.email if user else None,
                "amount": p.amount,
                "tax_amount": participant_tax,
                "status": p.status,
                "is_creator": p.is_creator,
            })

        return {
            "id": expense.id,
            "description": expense.description,
            "date": expense.date,
            "category": expense.category,
            "is_shared": True,
            "tax": expense.tax,
            "amount": None,
            "total_amount": expense.amount,
            "participants": participant_list,
        }