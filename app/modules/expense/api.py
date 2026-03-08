from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User
from .schema import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from .service import ExpenseService
from app.dependencies import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=ExpenseResponse, status_code=201)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ExpenseService.create_expense(db, expense, current_user)


@router.get("/", response_model=List[ExpenseResponse])
def get_all_expenses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ExpenseService.get_all_expenses(db, current_user)


@router.get("/user/{user_id}", response_model=List[ExpenseResponse])
def get_expenses_by_user(user_id: int, db: Session = Depends(get_db)):
    return ExpenseService.get_expenses_by_user(db, user_id)


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    return ExpenseService.get_expense_by_id(db, expense_id)


@router.patch("/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, expense: ExpenseUpdate, db: Session = Depends(get_db)):
    return ExpenseService.update_expense(db, expense_id, expense)


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    ExpenseService.delete_expense(db, expense_id)