from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from .schema import CategoryCreate, CategoryUpdate, CategoryResponse
from .service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return CategoryService.create_category(db, category)


@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    return CategoryService.get_all_categories(db)


@router.get("/user/{user_id}", response_model=List[CategoryResponse])
def get_categories_by_user(user_id: int, db: Session = Depends(get_db)):
    return CategoryService.get_categories_by_user(db, user_id)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return CategoryService.get_category_by_id(db, category_id)


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    return CategoryService.update_category(db, category_id, category)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    CategoryService.delete_category(db, category_id)