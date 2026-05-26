"""Verify new Supabase columns exist"""
from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env.local')
import psycopg2

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute("""
    SELECT column_name FROM information_schema.columns
    WHERE table_name='products'
    AND column_name IN ('expiry_date','batch_number','size_variants','model_number','warranty_months','shade','gender','archived')
    ORDER BY column_name
""")
prod_cols = [r[0] for r in cur.fetchall()]

cur.execute("""
    SELECT column_name FROM information_schema.columns
    WHERE table_name='shops'
    AND column_name IN ('business_type','setup_complete')
    ORDER BY column_name
""")
shop_cols = [r[0] for r in cur.fetchall()]
cur.close(); conn.close()

print('Product extended columns:', prod_cols)
print('Shop business columns:', shop_cols)
if len(prod_cols) == 8 and len(shop_cols) == 2:
    print('SUCCESS: All 10 new columns verified in Supabase!')
else:
    print(f'WARNING: Expected 10 columns, found {len(prod_cols)+len(shop_cols)}')
