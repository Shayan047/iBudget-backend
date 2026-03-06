from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class IncomeCreate(BaseModel):
    user_id: int
    amount: float
    date: Optional[datetime] = None


class IncomeUpdate(BaseModel):
    amount: Optional[float] = None
    date: Optional[datetime] = None


class IncomeResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    date: datetime

    class Config:
        from_attributes = True


class IncomeListResponse(BaseModel):
    incomes: List[IncomeResponse]