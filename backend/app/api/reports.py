from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database.database import get_db
from ..models import models
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    today = datetime.now().date()
    
    today_sales = db.query(func.sum(models.Sale.total_amount)).filter(func.date(models.Sale.created_at) == today).scalar() or 0
    today_profit = db.query(func.sum(models.Sale.total_profit)).filter(func.date(models.Sale.created_at) == today).scalar() or 0
    total_udhar = db.query(func.sum(models.Customer.total_due)).scalar() or 0
    low_stock_count = db.query(models.Product).filter(models.Product.current_stock <= models.Product.min_stock).count()

    return {
        "today_sales": today_sales,
        "today_profit": today_profit,
        "total_udhar": total_udhar,
        "low_stock_count": low_stock_count
    }

@router.get("/sales-trend")
def get_sales_trend(db: Session = Depends(get_db)):
    # Last 7 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    
    results = db.query(
        func.date(models.Sale.created_at).label('date'),
        func.sum(models.Sale.total_amount).label('total')
    ).filter(func.date(models.Sale.created_at) >= start_date).group_by(func.date(models.Sale.created_at)).all()
    
    return [{"date": r.date.strftime("%Y-%m-%d"), "total": r.total} for r in results]
