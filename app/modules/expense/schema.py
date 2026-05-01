from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List
from app.models import SharedExpenseStatus


# ── Category ──────────────────────────────────────────────────


class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# ── Tax ───────────────────────────────────────────────────────


class TaxResponse(BaseModel):
    id: int
    amount: float

    class Config:
        from_attributes = True


# ── Personal expense ──────────────────────────────────────────


class ExpenseCreate(BaseModel):
    category_id: int
    amount: float
    description: str | None = None
    date: datetime | None = None
    tax_amount: float | None = None


class ExpenseUpdate(BaseModel):
    category_id: int | None = None
    amount: float | None = None
    description: str | None = None
    date: datetime | None = None
    tax_amount: float | None = None


# ── Shared expense ────────────────────────────────────────────


class SharedExpenseUserCreate(BaseModel):
    email: EmailStr
    amount: float


class SharedExpenseCreate(BaseModel):
    category_id: int
    total_amount: float
    my_share: float
    description: str | None = None
    date: datetime | None = None
    tax_amount: float | None = None
    users: List[SharedExpenseUserCreate]


class SharedExpenseUserUpdateItem(BaseModel):
    email: EmailStr
    amount: float
    status: SharedExpenseStatus


class SharedExpenseUpdate(BaseModel):
    category_id: int | None = None
    total_amount: float | None = None
    my_share: float | None = None
    description: str | None = None
    date: datetime | None = None
    tax_amount: float | None = None
    users: List[SharedExpenseUserUpdateItem] | None = None


class ParticipantResponse(BaseModel):
    id: int
    user_id: int
    user_name: str | None
    user_email: str | None
    amount: float
    tax_amount: float | None
    status: SharedExpenseStatus
    is_creator: bool

    class Config:
        from_attributes = True


class ExpenseSummaryResponse(BaseModel):
    id: int
    description: str | None
    my_amount: float
    date: datetime
    category: CategoryResponse | None
    is_shared: bool
    is_creator: bool | None = None
    status: SharedExpenseStatus | None = None

    class Config:
        from_attributes = True


class ExpenseDetailResponse(BaseModel):
    id: int
    description: str | None
    date: datetime
    category: CategoryResponse | None
    is_shared: bool
    tax: TaxResponse | None
    amount: float | None = None
    total_amount: float | None = None
    participants: List[ParticipantResponse] | None = None

    class Config:
        from_attributes = True
