from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from .database.database import engine, Base, get_db
from .api import auth, products, billing, customers, reports, shop, notifications, payments, referrals, support, dukandar, admin
from .models import models
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure all models are registered with Base then create tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully")
except Exception as e:
    logger.error(f"Failed to create tables: {e}")

# ── DB migration: add missing columns to existing tables ──────────
def _migrate():
    """Check & add missing columns — each in its own autocommit connection."""
    from sqlalchemy import inspect as sa_inspect
    migrates = [
        # (table, column, type_def)
        ("users", "full_name", "VARCHAR"),
        ("users", "is_active", "INTEGER DEFAULT 1"),
        ("shops", "mobile", "VARCHAR"),
        ("shops", "business_type", "VARCHAR"),
        ("shops", "logo_url", "VARCHAR"),
        ("shops", "setup_complete", "INTEGER DEFAULT 0"),
        ("shops", "subscription_plan", "VARCHAR DEFAULT 'starter'"),
        ("shops", "subscription_status", "VARCHAR DEFAULT 'active'"),
        ("shops", "subscription_expiry", "TIMESTAMP"),
        ("shops", "subscription_cancelled_at", "TIMESTAMP"),
        ("shops", "cancellation_reason", "VARCHAR"),
        ("products", "expiry_date", "VARCHAR"),
    ]
    try:
        insp = sa_inspect(engine)
        for table, col, type_def in migrates:
            if col not in [c["name"] for c in insp.get_columns(table)]:
                with engine.connect() as conn:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {type_def}"))
                    conn.commit()
                    logger.info(f"Added column {table}.{col}")
    except Exception as e:
        logger.warning(f"DB migration note: {e}")

_migrate()

app = FastAPI(title="Kirana Smart Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", ""),
        os.getenv("LANDING_URL", ""),
        "https://kirana-manager-frontend.onrender.com",
        "https://kirana-manager.onrender.com",
        "https://kirana-backend.onrender.com",
        "https://kirana-manager-landing-page.onrender.com",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["billing"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["customers"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(shop.router, prefix="/api/v1/shop", tags=["shop"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(referrals.router, prefix="/api/v1/referrals", tags=["referrals"])
app.include_router(support.router, prefix="/api/v1/support", tags=["support"])
app.include_router(dukandar.router, prefix="/api/v1/dukandar", tags=["dukandar"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "Kirana Smart Dashboard API is running"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar()
        tables = inspect(engine).get_table_names()
        return {"status": "ok", "db": "connected", "tables": tables}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
