from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from .schema import BudgetCreate, BudgetUpdate, BudgetResponse
from .service import BudgetService
from app.models import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("/", response_model=List[BudgetResponse])
def get_all_budgets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return BudgetService.get_all_budgets(db, current_user)


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(budget_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return BudgetService.get_budget_by_id(db, budget_id, current_user)


@router.post("/", response_model=BudgetResponse, status_code=201)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return BudgetService.create_budget(db, budget, current_user)


@router.patch("/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, budget: BudgetUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return BudgetService.update_budget(db, budget_id, budget, current_user)


@router.delete("/{budget_id}", status_code=200)
def delete_budget(budget_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return BudgetService.delete_budget(db, budget_id, current_user)