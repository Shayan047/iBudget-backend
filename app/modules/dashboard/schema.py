from pydantic import BaseModel
from typing import List
from datetime import datetime

class ExpenseItem(BaseModel):
    id: int
    amount: float
    date: datetime
    category_name: str | None = None

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    month: int
    year: int
    total_income: float
    total_expenses: float
    budget: float
    remaining_balance: float
    expenses: List[ExpenseItem]