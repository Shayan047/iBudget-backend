from pydantic import BaseModel
from app.utils.pagination import PaginationMeta
from typing import List


class TaxCreate(BaseModel):
    amount: float
    expense_id: int | None = None
    income_id: int | None = None


class TaxResponse(BaseModel):
    id: int
    amount: float
    expense_id: int | None
    income_id: int | None
    is_derived: bool = False
    my_tax_amount: float | None
    description: str | None = None

    class Config:
        from_attributes = True


class PaginatedTaxResponse(BaseModel):
    data: List[TaxResponse]
    pagination: PaginationMeta
