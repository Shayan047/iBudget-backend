from datetime import datetime
from enum import Enum

from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Boolean,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SharedExpenseStatus(str, Enum):
    paid = "paid"
    pending = "pending"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    incomes: Mapped[list["Income"]] = relationship(
        back_populates="user", cascade="all, delete"
    )
    budgets: Mapped[list["Budget"]] = relationship(
        back_populates="user", cascade="all, delete"
    )
    categories: Mapped[list["Category"]] = relationship(
        back_populates="created_by_user"
    )
    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="user", cascade="all, delete"
    )
    shared_expense_users: Mapped[list["SharedExpenseUser"]] = relationship(
        back_populates="user", cascade="all, delete"
    )


class Tax(Base):
    __tablename__ = "taxes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)

    expense_id: Mapped[int | None] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE"), nullable=True
    )
    income_id: Mapped[int | None] = mapped_column(
        ForeignKey("incomes.id", ondelete="CASCADE"), nullable=True
    )

    expense: Mapped["Expense | None"] = relationship(back_populates="tax")
    income: Mapped["Income | None"] = relationship(back_populates="tax")


class Income(Base):
    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="incomes")
    tax: Mapped["Tax | None"] = relationship(back_populates="income", uselist=False)


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="budgets")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )

    created_by_user: Mapped["User"] = relationship(back_populates="categories")
    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="category", cascade="all, delete"
    )


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE")
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="expenses")
    category: Mapped["Category"] = relationship(back_populates="expenses")
    tax: Mapped["Tax | None"] = relationship(back_populates="expense", uselist=False)
    shared_expense_users: Mapped[list["SharedExpenseUser"]] = relationship(
        back_populates="expense", cascade="all, delete"
    )


class SharedExpenseUser(Base):
    __tablename__ = "shared_expense_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[SharedExpenseStatus] = mapped_column(
        SQLEnum(SharedExpenseStatus), nullable=False
    )
    is_creator: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    expense: Mapped["Expense"] = relationship(back_populates="shared_expense_users")
    user: Mapped["User"] = relationship(back_populates="shared_expense_users")
