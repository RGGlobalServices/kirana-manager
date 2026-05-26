from sqlalchemy import create_engine, text, inspect
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid

# Load from root .env.local
root_env = Path(__file__).resolve().parent.parent / ".env.local"
load_dotenv(dotenv_path=root_env)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

tables_to_drop = [
    "sale_items",
    "sales",
    "customer_transactions",
    "customers",
    "products",
    "shops",
    "users",
    "udhar_transactions",
    "udhar_customers"
]

with engine.connect() as conn:
    print("Dropping tables...")
    for table in tables_to_drop:
        try:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            print(f"Dropped {table}")
        except Exception as e:
            print(f"Failed to drop {table}: {e}")
    conn.commit()

# Now recreate using models
from app.models.models import Base
print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done creating tables.")

# Inspect columns of 'users'
inspector = inspect(engine)
columns = inspector.get_columns('users')
print("\nUsers table columns:")
for col in columns:
    print(f"  {col['name']}: {col['type']}")
