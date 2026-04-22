from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from app.models import (
    Expense,
    SharedExpenseUser,
    SharedExpenseStatus,
    Category,
    User,
)
from .schema import (
    ExpenseCreate,
    ExpenseUpdate,
    SharedExpenseCreate,
    SharedExpenseUpdate,
)


class ExpenseService:

    # ── Get all (summary list) ────────────────────────────────────

    @staticmethod
    def get_all_expenses(db: Session, current_user: User) -> list:
        results = []

        # 1. Personal expenses (not shared)
        personal = (
            db.query(Expense)
            .filter(
                Expense.user_id == current_user.id,
                Expense.is_shared == False,
            )
            .all()
        )
        for exp in personal:
            results.append(
                {
                    "id": exp.id,
                    "description": exp.description,
                    "my_amount": exp.amount,
                    "date": exp.date,
                    "category": exp.category,
                    "is_shared": False,
                    "is_creator": None,
                    "status": None,
                }
            )

        # 2. Shared expenses (as creator OR participant)
        shared_entries = (
            db.query(SharedExpenseUser)
            .filter(SharedExpenseUser.user_id == current_user.id)
            .all()
        )
        for entry in shared_entries:
            exp = entry.expense
            results.append(
                {
                    "id": exp.id,
                    "description": exp.description,
                    "my_amount": entry.amount,
                    "date": exp.date,
                    "category": exp.category,
                    "is_shared": True,
                    "is_creator": entry.is_creator,  # ← added
                    "status": entry.status,  # ← added
                }
            )

        return results

    # ── Get single expense detail ─────────────────────────────────

    @staticmethod
    def get_expense_by_id(db: Session, expense_id: int, current_user: User) -> dict:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        if expense.is_shared:
            # Verify user is creator or participant
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

    # ── Create personal expense ───────────────────────────────────

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
        db.commit()
        db.refresh(expense)
        return ExpenseService._format_personal_detail(expense)

    # ── Create shared expense ─────────────────────────────────────

    @staticmethod
    def create_shared_expense(
        db: Session, data: SharedExpenseCreate, current_user: User
    ) -> dict:
        # Step 1 — Validate all participant emails exist first
        participants = []
        for entry in data.users:
            user = db.query(User).filter(User.email == entry.email).first()
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail=f"User with email '{entry.email}' not found",
                )
            participants.append((user, entry.amount))

        # Step 2 — Validate shares add up to total
        total_shares = round(data.my_share + sum(u.amount for u in data.users), 2)
        if total_shares != round(data.total_amount, 2):
            raise HTTPException(
                status_code=400,
                detail=f"Shares ({total_shares}) do not match total amount ({data.total_amount})",
            )

        # Step 3 — Validate category
        category = db.query(Category).filter(Category.id == data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        # Step 4 — Create expense
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

        # Step 5 — Add creator as SharedExpenseUser with is_creator=True
        db.add(
            SharedExpenseUser(
                expense_id=expense.id,
                user_id=current_user.id,
                amount=data.my_share,
                status=SharedExpenseStatus.paid,
                is_creator=True,
            )
        )

        # Step 6 — Add participants
        for user, amount in participants:
            db.add(
                SharedExpenseUser(
                    expense_id=expense.id,
                    user_id=user.id,
                    amount=amount,
                    status=SharedExpenseStatus.pending,
                    is_creator=False,
                )
            )

        db.commit()
        db.refresh(expense)
        return ExpenseService._format_shared_detail(db, expense)

    # ── Update personal expense ───────────────────────────────────

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
            category = (
                db.query(Category).filter(Category.id == data.category_id).first()
            )
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
            expense.category_id = data.category_id
        if data.amount is not None:
            expense.amount = data.amount
        if data.description is not None:
            expense.description = data.description
        if data.date is not None:
            expense.date = data.date

        db.commit()
        db.refresh(expense)
        return ExpenseService._format_personal_detail(expense)

    # ── Update shared expense ─────────────────────────────────────

    @staticmethod
    def update_shared_expense(
        db: Session, expense_id: int, data: SharedExpenseUpdate, current_user: User
    ) -> dict:
        # Verify expense exists and current user is the creator
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

        # Validate all participant emails exist before making any changes
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

            # Validate shares add up to total
            total_amount = (
                data.total_amount if data.total_amount is not None else expense.amount
            )
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

        # Step 1 — Update expense fields
        if data.category_id is not None:
            category = (
                db.query(Category).filter(Category.id == data.category_id).first()
            )
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
            expense.category_id = data.category_id
        if data.total_amount is not None:
            expense.amount = data.total_amount
        if data.description is not None:
            expense.description = data.description
        if data.date is not None:
            expense.date = data.date

        db.flush()

        # Step 2 — Delete all existing participants and re-add
        if data.users is not None:
            db.query(SharedExpenseUser).filter(
                SharedExpenseUser.expense_id == expense_id
            ).delete()
            db.flush()

            # Re-add creator
            db.add(
                SharedExpenseUser(
                    expense_id=expense.id,
                    user_id=current_user.id,
                    amount=data.my_share,
                    status=SharedExpenseStatus.paid,
                    is_creator=True,
                )
            )

            # Re-add participants
            for user, amount, status in new_participants:
                db.add(
                    SharedExpenseUser(
                        expense_id=expense.id,
                        user_id=user.id,
                        amount=amount,
                        status=status,
                        is_creator=False,
                    )
                )

        db.commit()
        db.refresh(expense)
        return ExpenseService._format_shared_detail(db, expense)

    # ── Delete expense ────────────────────────────────────────────

    @staticmethod
    def delete_expense(db: Session, expense_id: int, current_user: User) -> dict:
        expense = (
            db.query(Expense)
            .filter(
                Expense.id == expense_id,
            )
            .first()
        )
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        elif expense.is_shared and expense.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this shared expense"
            )

        db.delete(expense)
        db.commit()
        return {"status": "Success", "message": "Expense deleted successfully"}

    # ── Private helpers ───────────────────────────────────────────

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

        participant_list = []
        for p in participants:
            user = db.query(User).filter(User.id == p.user_id).first()
            participant_tax = (
                round((p.amount / expense.amount) * tax_amount, 2)
                if tax_amount
                else None
            )
            participant_list.append(
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "user_name": user.name if user else None,
                    "user_email": user.email if user else None,
                    "amount": p.amount,
                    "tax_amount": participant_tax,
                    "status": p.status,
                    "is_creator": p.is_creator,
                }
            )

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
