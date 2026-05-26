from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import os

# Load from root .env.local (one level above backend/)
_root_env = Path(__file__).resolve().parent.parent.parent / ".env.local"
if _root_env.exists():
    load_dotenv(dotenv_path=_root_env, override=False)

from .database.database import engine, Base
from .api import auth, products, billing, customers, reports, shop, notifications, payments, support, referrals, dukandar, admin

app = FastAPI(title="Vyapar Sarthi Dashboard API")

# Build allowed origins: explicit list required when allow_credentials=True
# (browsers reject wildcard "*" combined with credentials)
_app_url = os.getenv("APP_URL", "http://localhost:3000").rstrip("/")
_allowed_origins = list({
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    _app_url,
})

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Start background notification scheduler
    import asyncio
    from .tasks import run_daily_notifications

    async def notification_scheduler():
        while True:
            try:
                now = datetime.now()
                if now.minute == 0:
                    if now.hour == 8:
                        await asyncio.to_thread(run_daily_notifications)
            except Exception as e:
                print(f"Scheduler error: {e}")
            await asyncio.sleep(60)

    asyncio.create_task(notification_scheduler())

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["billing"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["customers"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(shop.router, prefix="/api/v1/shop", tags=["shop"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(payments.router,     prefix="/api/v1/payments",      tags=["payments"])
app.include_router(support.router,      prefix="/api/v1/support",       tags=["support"])
app.include_router(referrals.router,    prefix="/api/v1/referrals",     tags=["referrals"])
app.include_router(dukandar.router,     prefix="/api/v1/dukandar",      tags=["dukandar"])
app.include_router(admin.router,        prefix="/api/v1/admin",         tags=["admin"])

@app.get("/")
async def root():
    return {"message": "Vyapar Sarthi Dashboard API is running"}
