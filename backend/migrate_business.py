"""
Universal Vyapar Sarthi — Supabase Migration Script
Run: python migrate_business.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv

_root_env = Path(__file__).resolve().parent.parent / ".env.local"
load_dotenv(dotenv_path=_root_env)

import psycopg2

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("ERROR: DATABASE_URL not found in .env.local")
    exit(1)

print(f"Connecting to: {db_url[:40]}...")

conn = psycopg2.connect(db_url)
cur = conn.cursor()

migrations = [
    # Shops - business type & setup flag
    "ALTER TABLE shops ADD COLUMN IF NOT EXISTS business_type VARCHAR DEFAULT 'kirana'",
    "ALTER TABLE shops ADD COLUMN IF NOT EXISTS setup_complete BOOLEAN DEFAULT false",
    # Products - expiry / medical
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS expiry_date VARCHAR",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS batch_number VARCHAR",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS drug_schedule VARCHAR",
    # Products - electronics
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS model_number VARCHAR",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS warranty_months INTEGER",
    # Products - fashion (shoes/clothes)
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS gender VARCHAR",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS size_variants TEXT",
    # Products - cosmetics
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS shade VARCHAR",
    # Products - general
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT false",
    # Sales - invoice number
    "ALTER TABLE sales ADD COLUMN IF NOT EXISTS invoice_number VARCHAR UNIQUE",
    # Shops - subscription management
    "ALTER TABLE shops ADD COLUMN IF NOT EXISTS subscription_plan VARCHAR DEFAULT 'starter'",
    "ALTER TABLE shops ADD COLUMN IF NOT EXISTS subscription_status VARCHAR DEFAULT 'active'",
    "ALTER TABLE shops ADD COLUMN IF NOT EXISTS subscription_expiry TIMESTAMP WITH TIME ZONE",
]

success = 0
for sql in migrations:
    try:
        cur.execute(sql)
        print(f"  OK: {sql[:70]}")
        success += 1
    except Exception as e:
        print(f"  SKIP (already exists?): {e}")

conn.commit()
cur.close()
conn.close()
print(f"\nMigration complete! {success}/{len(migrations)} columns applied.")
