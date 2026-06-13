from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.utils.pagination import PaginationMeta


class TaxResponse(BaseModel):
    id: int
    amount: float

    class Config:
        from_attributes = True


class IncomeCreate(BaseModel):
    amount: float
    description: str
    date: Optional[datetime] = None
    tax_amount: float | None = None


class IncomeUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    tax_amount: float | None = None


class IncomeResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    description: str | None
    date: datetime
    tax: TaxResponse | None = None

    class Config:
        from_attributes = True


class PaginatedIncomeResponse(BaseModel):
    data: List[IncomeResponse]
    pagination: PaginationMeta
