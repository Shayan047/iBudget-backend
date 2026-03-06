from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from .schema import IncomeCreate, IncomeUpdate, IncomeResponse
from .service import IncomeService

router = APIRouter(prefix="/incomes", tags=["Incomes"])


@router.post("/", response_model=IncomeResponse, status_code=201)
def create_income(income: IncomeCreate, db: Session = Depends(get_db)):
    return IncomeService.create_income(db, income)


@router.get("/", response_model=List[IncomeResponse])
def get_all_incomes(db: Session = Depends(get_db)):
    return IncomeService.get_all_incomes(db)


@router.get("/user/{user_id}", response_model=List[IncomeResponse])
def get_incomes_by_user(user_id: int, db: Session = Depends(get_db)):
    return IncomeService.get_incomes_by_user(db, user_id)


@router.get("/{income_id}", response_model=IncomeResponse)
def get_income(income_id: int, db: Session = Depends(get_db)):
    return IncomeService.get_income_by_id(db, income_id)


@router.patch("/{income_id}", response_model=IncomeResponse)
def update_income(income_id: int, income: IncomeUpdate, db: Session = Depends(get_db)):
    return IncomeService.update_income(db, income_id, income)


@router.delete("/{income_id}", status_code=204)
def delete_income(income_id: int, db: Session = Depends(get_db)):
    IncomeService.delete_income(db, income_id)