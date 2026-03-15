from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from .schema import IncomeCreate, IncomeUpdate, IncomeResponse
from .service import IncomeService
from app.models import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/incomes", tags=["Incomes"])


@router.get("/", response_model=List[IncomeResponse])
def get_all_incomes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return IncomeService.get_all_incomes(db, current_user)


@router.get("/{income_id}", response_model=IncomeResponse)
def get_income(income_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return IncomeService.get_income_by_id(db, income_id, current_user)


@router.post("/", response_model=IncomeResponse, status_code=201)
def create_income(income: IncomeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return IncomeService.create_income(db, income, current_user)


@router.patch("/{income_id}", response_model=IncomeResponse)
def update_income(income_id: int, income: IncomeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return IncomeService.update_income(db, income_id, income, current_user)


@router.delete("/{income_id}", status_code=200)
def delete_income(income_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return IncomeService.delete_income(db, income_id, current_user)