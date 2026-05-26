from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv

# Load from root .env.local (one level above backend/)
_root_env = Path(__file__).resolve().parent.parent.parent.parent / ".env.local"
if _root_env.exists():
    load_dotenv(dotenv_path=_root_env, override=False)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kirana.db")

# psycopg2 does not accept check_same_thread (SQLite-only arg)
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
