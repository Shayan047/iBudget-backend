from app.database import engine
from app.models import Base
from app.seed.main import run_seed


def reset_db():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("Running seeders (Generating 10 users + 3 months history)...")
    try:
        run_seed()
        print("Database reset and seeded successfully!")
    except Exception as e:
        print(f"Seeding failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    reset_db()
