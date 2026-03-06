from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from .schema import BudgetCreate, BudgetUpdate, BudgetResponse
from .service import BudgetService

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("/", response_model=BudgetResponse, status_code=201)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    return BudgetService.create_budget(db, budget)


@router.get("/", response_model=List[BudgetResponse])
def get_all_budgets(db: Session = Depends(get_db)):
    return BudgetService.get_all_budgets(db)


@router.get("/user/{user_id}", response_model=List[BudgetResponse])
def get_budgets_by_user(user_id: int, db: Session = Depends(get_db)):
    return BudgetService.get_budgets_by_user(db, user_id)


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    return BudgetService.get_budget_by_id(db, budget_id)


@router.patch("/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, budget: BudgetUpdate, db: Session = Depends(get_db)):
    return BudgetService.update_budget(db, budget_id, budget)


@router.delete("/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    BudgetService.delete_budget(db, budget_id)