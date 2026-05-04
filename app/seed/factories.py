import factory
import random
from factory.alchemy import SQLAlchemyModelFactory
from app.database import SessionLocal
from app.models import User, Category, Expense, Income, Budget, Tax
from app.utils.hashing import hash_password


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = SessionLocal()
        sqlalchemy_session_persistence = "commit"


class UserFactory(BaseFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    name = factory.Faker("name")
    password = factory.LazyFunction(lambda: hash_password("password123"))


class CategoryFactory(BaseFactory):
    class Meta:
        model = Category

    name = factory.Iterator(
        ["Rent", "Groceries", "Food", "Transport", "Entertainment", "Health"]
    )


class IncomeFactory(BaseFactory):
    class Meta:
        model = Income

    amount = factory.Faker(
        "pyfloat",
        left_digits=4,
        right_digits=2,
        positive=True,
        min_value=3000,
        max_value=8000,
    )
    description = "Monthly Salary"


class ExpenseFactory(BaseFactory):
    class Meta:
        model = Expense

    amount = factory.Faker(
        "pyfloat",
        left_digits=3,
        right_digits=2,
        positive=True,
        min_value=10,
        max_value=200,
    )
    description = factory.Faker("sentence", nb_words=4)
    is_shared = False


class BudgetFactory(BaseFactory):
    class Meta:
        model = Budget

    amount = factory.Faker(
        "pyfloat",
        left_digits=4,
        right_digits=2,
        positive=True,
        min_value=1000,
        max_value=5000,
    )


class TaxFactory(BaseFactory):
    class Meta:
        model = Tax

    amount = factory.Faker(
        "pyfloat",
        left_digits=2,
        right_digits=2,
        positive=True,
        min_value=1,
        max_value=50,
    )
