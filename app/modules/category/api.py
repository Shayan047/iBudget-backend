from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from .schema import CategoryCreate, CategoryUpdate, CategoryResponse
from .service import CategoryService
from app.models import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CategoryService.get_all_categories(db, current_user)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CategoryService.get_category_by_id(db, category_id, current_user)


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CategoryService.create_category(db, category, current_user)


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CategoryService.update_category(db, category_id, category, current_user)


@router.delete("/{category_id}", status_code=200)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CategoryService.delete_category(db, category_id, current_user)