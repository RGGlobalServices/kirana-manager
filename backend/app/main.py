from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database.database import engine, Base, get_db
from .api import auth, products, billing, customers, reports
from .models import models
import os
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Kirana Smart Dashboard API")

@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Tables created successfully")
    except Exception as e:
        logging.error(f"Failed to create tables: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", ""),
        os.getenv("LANDING_URL", ""),
        "https://kirana-manager-fronend.onrender.com",
        "https://kirana-manager.onrender.com",
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

@app.get("/")
async def root():
    return {"message": "Kirana Smart Dashboard API is running"}
