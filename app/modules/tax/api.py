from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.dependencies import get_current_user
from .service import TaxService
from .schema import TaxCreate, TaxResponse

router = APIRouter(prefix="/taxes", tags=["Taxes"])


@router.get("/", response_model=List[TaxResponse])
def get_all_taxes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaxService.get_all_taxes(db, current_user)


@router.get("/{tax_id}", response_model=TaxResponse)
def get_tax(
    tax_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaxService.get_tax_by_id(db, tax_id, current_user)


@router.post("/", response_model=TaxResponse, status_code=201)
def create_tax(
    data: TaxCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return TaxService.create_tax(db, data, current_user)


@router.delete("/{tax_id}", status_code=204)
def delete_tax(
    tax_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    TaxService.delete_tax(db, tax_id, current_user)
