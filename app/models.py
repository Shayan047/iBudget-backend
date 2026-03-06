from datetime import datetime
from enum import Enum

from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# =========================
# Base
# =========================
class Base(DeclarativeBase):
    pass


# =========================
# Enum
# =========================
class SharedExpenseStatus(str, Enum):
    paid = "paid"
    pending = "pending"


# =========================
# User
# =========================
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    incomes: Mapped[list["Income"]] = relationship(back_populates="user", cascade="all, delete")
    budgets: Mapped[list["Budget"]] = relationship(back_populates="user", cascade="all, delete")
    categories: Mapped[list["Category"]] = relationship(back_populates="created_by_user")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="user", cascade="all, delete")
    shared_expenses: Mapped[list["SharedExpense"]] = relationship(back_populates="user", cascade="all, delete")
    shared_expense_users: Mapped[list["SharedExpenseUser"]] = relationship(back_populates="user", cascade="all, delete")


# =========================
# Income
# =========================
class Income(Base):
    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="incomes")
    taxes: Mapped[list["Tax"]] = relationship(back_populates="income", cascade="all, delete")


# =========================
# Budget
# =========================
class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="budgets")


# =========================
# Category
# =========================
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    created_by_user: Mapped["User"] = relationship(back_populates="categories")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="category", cascade="all, delete")


# =========================
# Expense
# =========================
class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="expenses")
    category: Mapped["Category"] = relationship(back_populates="expenses")
    taxes: Mapped[list["Tax"]] = relationship(back_populates="expense", cascade="all, delete")
    shared_expenses: Mapped[list["SharedExpense"]] = relationship(back_populates="expense", cascade="all, delete")


# =========================
# Tax
# =========================
class Tax(Base):
    __tablename__ = "taxes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    expense_id: Mapped[int | None] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE"),
        nullable=True,
    )

    income_id: Mapped[int | None] = mapped_column(
        ForeignKey("incomes.id", ondelete="CASCADE"),
        nullable=True,
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)

    expense: Mapped["Expense"] = relationship(back_populates="taxes")
    income: Mapped["Income"] = relationship(back_populates="taxes")


# =========================
# SharedExpense
# =========================
class SharedExpense(Base):
    __tablename__ = "shared_expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship(back_populates="shared_expenses")
    expense: Mapped["Expense"] = relationship(back_populates="shared_expenses")

    shared_expense_users: Mapped[list["SharedExpenseUser"]] = relationship(
        back_populates="shared_expense",
        cascade="all, delete"
    )


# =========================
# SharedExpenseUser
# =========================
class SharedExpenseUser(Base):
    __tablename__ = "shared_expense_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    shared_expense_id: Mapped[int] = mapped_column(
        ForeignKey("shared_expenses.id", ondelete="CASCADE")
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[SharedExpenseStatus] = mapped_column(
        SQLEnum(SharedExpenseStatus),
        nullable=False,
    )

    shared_expense: Mapped["SharedExpense"] = relationship(back_populates="shared_expense_users")
    user: Mapped["User"] = relationship(back_populates="shared_expense_users")