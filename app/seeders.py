from app.database import SessionLocal
from app.models import User, Category
from app.utils.hashing import hash_password

def seed_users(db):
    users = [
        User(email="alice@example.com", password=hash_password("alice123"), name="Alice"),
        User(email="bob@example.com", password=hash_password("bob123"), name="Bob"),
    ]
    db.add_all(users)
    db.commit()
    print("Users seeded")


def seed_categories(db):
    categories = [
        Category(name="Rent"),
        Category(name="Groceries"),
        Category(name="Food"),
        Category(name="Transport"),
        Category(name="Entertainment"),
        Category(name="Health"),
    ]
    db.add_all(categories)
    db.commit()
    print("Categories seeded")


def run_seeds():
    db = SessionLocal()
    try:
        seed_users(db)
        seed_categories(db)
    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_seeds()