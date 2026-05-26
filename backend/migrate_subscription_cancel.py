"""
Migration: add subscription_cancelled_at and cancellation_reason to shops table.
Run once: python migrate_subscription_cancel.py
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'kirana.db')

def run():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    existing = {row[1] for row in cur.execute("PRAGMA table_info(shops)")}

    added = []
    if 'subscription_cancelled_at' not in existing:
        cur.execute("ALTER TABLE shops ADD COLUMN subscription_cancelled_at DATETIME")
        added.append('subscription_cancelled_at')
    if 'cancellation_reason' not in existing:
        cur.execute("ALTER TABLE shops ADD COLUMN cancellation_reason TEXT")
        added.append('cancellation_reason')

    conn.commit()
    conn.close()

    if added:
        print(f"Added columns: {', '.join(added)}")
    else:
        print("Columns already exist - nothing to do.")

if __name__ == '__main__':
    run()
