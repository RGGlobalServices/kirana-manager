from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv
from pathlib import Path

# Load from root .env.local
root_env = Path(__file__).resolve().parent.parent / ".env.local"
load_dotenv(dotenv_path=root_env)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print("Tables in database:")
for table_name in inspector.get_table_names():
    print(f"\nTable: {table_name}")
    for column in inspector.get_columns(table_name):
        print(f"  Column: {column['name']} - {column['type']}")
