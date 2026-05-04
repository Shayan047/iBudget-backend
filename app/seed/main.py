import random
import calendar
from datetime import datetime, date
from app.database import SessionLocal
from app.models import SharedExpenseUser, SharedExpenseStatus
from app.seed.factories import (
    UserFactory,
    CategoryFactory,
    IncomeFactory,
    ExpenseFactory,
    BudgetFactory,
    TaxFactory,
)


def get_target_month_year(current_date, offset_months):
    """Helper to calculate past months without external libraries."""
    month = current_date.month - offset_months
    year = current_date.year
    while month <= 0:
        month += 12
        year -= 1
    return year, month


def run_seed():
    db = SessionLocal()
    print("Starting seeding process...")

    categories = CategoryFactory.create_batch(6)
    print(f"Created {len(categories)} categories.")

    users = UserFactory.create_batch(10)
    print("Created 10 users.")

    today = date.today()

    for user in users:
        for i in range(3):
            year, month = get_target_month_year(today, i)
            days_in_month = calendar.monthrange(year, month)[1]
            first_day_of_month = date(year, month, 1)

            BudgetFactory.create(user=user, date=first_day_of_month)

            num_incomes = random.randint(1, 3)
            for _ in range(num_incomes):
                income_date = datetime(year, month, random.randint(1, days_in_month))
                income = IncomeFactory.create(user=user, date=income_date)

                if random.random() < 0.5:
                    tax_amount = round(income.amount * random.uniform(0.10, 0.20), 2)
                    TaxFactory.create(income_id=income.id, amount=tax_amount)

            num_expenses = random.randint(40, 45)
            for _ in range(num_expenses):
                expense_date = datetime(year, month, random.randint(1, days_in_month))

                is_shared = random.random() < 0.18

                expense = ExpenseFactory.create(
                    user=user,
                    category=random.choice(categories),
                    date=expense_date,
                    is_shared=is_shared,
                )

                if random.random() < 0.6:
                    tax_amount = round(expense.amount * random.uniform(0.05, 0.10), 2)
                    TaxFactory.create(expense_id=expense.id, amount=tax_amount)

                if is_shared:
                    other_users = random.sample(
                        [u for u in users if u.id != user.id], 2
                    )
                    participants = [user] + other_users

                    part1 = round(random.uniform(10, expense.amount / 2), 2)
                    part2 = round(random.uniform(10, expense.amount - part1 - 10), 2)
                    part3 = round(expense.amount - part1 - part2, 2)
                    split_amounts = [part1, part2, part3]
                    random.shuffle(split_amounts)

                    for idx, participant in enumerate(participants):
                        is_creator = participant.id == user.id
                        status = (
                            SharedExpenseStatus.paid
                            if is_creator
                            else random.choice(list(SharedExpenseStatus))
                        )

                        share = SharedExpenseUser(
                            expense_id=expense.id,
                            user_id=participant.id,
                            amount=split_amounts[idx],
                            status=status,
                            is_creator=is_creator,
                        )
                        db.add(share)

    db.commit()
    db.close()
    print("Seeding complete!")
