from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Category, User
from .schema import CategoryCreate, CategoryUpdate


class CategoryService:

    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate) -> Category:
        if category_data.created_by_user_id is not None:
            user = db.query(User).filter(User.id == category_data.created_by_user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

        new_category = Category(
            name=category_data.name,
            created_by_user_id=category_data.created_by_user_id,
        )

        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return new_category

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Category:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        return category

    @staticmethod
    def get_all_categories(db: Session) -> list[Category]:
        return db.query(Category).all()

    @staticmethod
    def get_categories_by_user(db: Session, user_id: int) -> list[Category]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return db.query(Category).filter(Category.created_by_user_id == user_id).all()

    @staticmethod
    def update_category(db: Session, category_id: int, category_data: CategoryUpdate) -> Category:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        if category_data.name is not None:
            category.name = category_data.name

        db.commit()
        db.refresh(category)

        return category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> None:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        db.delete(category)
        db.commit()