from pydantic import BaseModel


class TaxCreate(BaseModel):
    amount: float
    expense_id: int | None = None
    income_id: int | None = None


class TaxResponse(BaseModel):
    id: int
    amount: float
    expense_id: int | None
    income_id: int | None
    is_derived: bool = False  # True = participant's calculated tax
    my_tax_amount: float | None  # participant's share of the tax

    class Config:
        from_attributes = True
