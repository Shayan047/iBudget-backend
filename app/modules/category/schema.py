from pydantic import BaseModel
from typing import List, Optional


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    created_by_user_id: Optional[int] = None

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]