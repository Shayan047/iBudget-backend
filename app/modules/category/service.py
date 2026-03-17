from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Category, User
from .schema import CategoryCreate, CategoryUpdate
from sqlalchemy import or_

class CategoryService:

    @staticmethod
    def get_all_categories(db: Session, current_user: User) -> list[Category]:
        return db.query(Category).filter(
            or_(
                Category.created_by_user_id == current_user.id,
                Category.created_by_user_id == None
            )
        ).all()


    @staticmethod
    def get_category_by_id(db: Session, category_id: int, current_user: User) -> Category:
        category = db.query(Category).filter(
            Category.id == category_id,
            Category.created_by_user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category


    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate, current_user: User) -> Category:
        category = Category(
            name=category_data.name,
            created_by_user_id=current_user.id
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category


    @staticmethod
    def update_category(db: Session, category_id: int, category_data: CategoryUpdate, current_user: User) -> Category:
        category = db.query(Category).filter(
            Category.id == category_id,
            Category.created_by_user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found or not editable")

        if category_data.name is not None:
            category.name = category_data.name

        db.commit()
        db.refresh(category)
        return category


    @staticmethod
    def delete_category(db: Session, category_id: int, current_user: User) -> None:
        category = db.query(Category).filter(
            Category.id == category_id,
            Category.created_by_user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found or not deletable")

        db.delete(category)
        db.commit()

        return {"status": "Success", "message": "Category deleted successfully"}