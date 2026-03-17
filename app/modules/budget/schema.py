from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class BudgetCreate(BaseModel):
    amount: float
    date: datetime


class BudgetUpdate(BaseModel):
    amount: Optional[float] = None
    date: Optional[datetime] = None


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    date: datetime

    class Config:
        from_attributes = True


class BudgetListResponse(BaseModel):
    budgets: List[BudgetResponse]
