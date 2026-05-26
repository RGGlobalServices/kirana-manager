from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from pathlib import Path

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
    "users"
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

print("Done!")
