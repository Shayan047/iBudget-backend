from app.database import engine, SessionLocal
from app.models import Base
from app.seeders import seed_users, seed_categories


def reset_db():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("Running seeders...")
    db = SessionLocal()
    try:
        seed_users(db)
        seed_categories(db)
        print("Done!")
    except Exception as e:
        db.rollback()
        print(f"Failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    reset_db()