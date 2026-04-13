from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User
from app.dependencies import get_current_user
from .service import ExpenseService
from .schema import (
    ExpenseCreate,
    ExpenseUpdate,
    SharedExpenseCreate,
    SharedExpenseUpdate,
    ExpenseSummaryResponse,
    ExpenseDetailResponse,
)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/", response_model=List[ExpenseSummaryResponse])
def get_all_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ExpenseService.get_all_expenses(db, current_user)


@router.get("/{expense_id}", response_model=ExpenseDetailResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ExpenseService.get_expense_by_id(db, expense_id, current_user)


@router.post("/", response_model=ExpenseDetailResponse, status_code=201)
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ExpenseService.create_expense(db, data, current_user)


@router.patch("/{expense_id}", response_model=ExpenseDetailResponse)
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ExpenseService.update_expense(db, expense_id, data, current_user)


@router.delete("/{expense_id}", status_code=200)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ExpenseService.delete_expense(db, expense_id, current_user)


@router.post("/shared", response_model=ExpenseDetailResponse, status_code=201)
def create_shared_expense(
    data: SharedExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ExpenseService.create_shared_expense(db, data, current_user)


# ── New shared expense update endpoint ───────────────────────
@router.patch("/shared/{expense_id}", response_model=ExpenseDetailResponse)
def update_shared_expense(
    expense_id: int,
    data: SharedExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ExpenseService.update_shared_expense(db, expense_id, data, current_user)
