from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# =========================
# Expense Schemas
# =========================

class ExpenseCreate(BaseModel):
    user_id: int
    category_id: int
    amount: float
    date: Optional[datetime] = None


class ExpenseUpdate(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[float] = None
    date: Optional[datetime] = None

class CategoryJoinedResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ExpenseResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    date: datetime
    category: CategoryJoinedResponse

    class Config:
        from_attributes = True


class ExpenseListResponse(BaseModel):
    expenses: List[ExpenseResponse]