"""
Top Products Analytics API endpoint
Returns top N products grouped by revenue, quantity, or category
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database.database import get_db
from ..models import models
from .deps import get_current_shop
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

# This will be included in reports.py — expose at /reports/top-products
def get_top_products_data(
    db: Session,
    shop_id,
    group_by: str = "revenue",
    limit: int = 10,
    days: int = 30,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    group_by: 'revenue' | 'quantity' | 'category' | 'udhar'
    """
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        except ValueError:
            start_dt = datetime.now() - timedelta(days=days)
            end_dt = datetime.now() + timedelta(days=1)
    else:
        start_dt = datetime.now() - timedelta(days=days)
        end_dt = datetime.now() + timedelta(days=1)

    if group_by == "udhar":
        # Top customers by udhar amount
        results = db.query(
            models.Customer.name,
            models.Customer.total_due.label("value"),
            models.Customer.mobile
        ).filter(
            models.Customer.shop_id == shop_id,
            models.Customer.total_due > 0
        ).order_by(models.Customer.total_due.desc()).limit(limit).all()

        items = [{"name": r.name, "value": float(r.value), "detail": r.mobile or ""} for r in results]
        total = sum(i["value"] for i in items)
        for item in items:
            item["percentage"] = round((item["value"] / total * 100), 1) if total > 0 else 0
        return {"items": items, "total": total, "currency": True}

    elif group_by == "category":
        results = db.query(
            models.Product.category,
            func.sum(
                models.SaleItem.quantity * models.SaleItem.price_per_unit
            ).label("revenue"),
            func.sum(models.SaleItem.quantity).label("qty")
        ).join(models.SaleItem).join(models.Sale).filter(
            models.Sale.shop_id == shop_id,
            models.Sale.created_at >= start_dt,
            models.Sale.created_at < end_dt
        ).group_by(models.Product.category)\
         .order_by(func.sum(models.SaleItem.quantity * models.SaleItem.price_per_unit).desc())\
         .limit(limit).all()

        items = [{"name": r.category, "value": float(r.revenue or 0), "qty": float(r.qty or 0), "detail": f"{int(r.qty or 0)} items"} for r in results]

    elif group_by == "quantity":
        results = db.query(
            models.Product.id,
            models.Product.name,
            models.Product.category,
            func.sum(models.SaleItem.quantity).label("qty"),
            func.sum(models.SaleItem.quantity * models.SaleItem.price_per_unit).label("revenue"),
            func.sum(models.SaleItem.quantity * models.SaleItem.margin_per_unit).label("profit")
        ).join(models.SaleItem).join(models.Sale).filter(
            models.Sale.shop_id == shop_id,
            models.Sale.created_at >= start_dt,
            models.Sale.created_at < end_dt
        ).group_by(models.Product.id, models.Product.name, models.Product.category)\
         .order_by(func.sum(models.SaleItem.quantity).desc())\
         .limit(limit).all()

        items = [{
            "id": str(r.id),
            "name": r.name,
            "value": float(r.qty or 0),
            "revenue": float(r.revenue or 0),
            "profit": float(r.profit or 0),
            "category": r.category,
            "detail": f"₹{float(r.revenue or 0):,.0f} revenue"
        } for r in results]

    else:  # revenue (default)
        results = db.query(
            models.Product.id,
            models.Product.name,
            models.Product.category,
            func.sum(models.SaleItem.quantity * models.SaleItem.price_per_unit).label("revenue"),
            func.sum(models.SaleItem.quantity).label("qty"),
            func.sum(models.SaleItem.quantity * models.SaleItem.margin_per_unit).label("profit")
        ).join(models.SaleItem).join(models.Sale).filter(
            models.Sale.shop_id == shop_id,
            models.Sale.created_at >= start_dt,
            models.Sale.created_at < end_dt
        ).group_by(models.Product.id, models.Product.name, models.Product.category)\
         .order_by(func.sum(models.SaleItem.quantity * models.SaleItem.price_per_unit).desc())\
         .limit(limit).all()

        items = [{
            "id": str(r.id),
            "name": r.name,
            "value": float(r.revenue or 0),
            "qty": float(r.qty or 0),
            "profit": float(r.profit or 0),
            "category": r.category,
            "detail": f"{int(r.qty or 0)} units sold"
        } for r in results]

    total = sum(i["value"] for i in items)
    for item in items:
        item["percentage"] = round((item["value"] / total * 100), 1) if total > 0 else 0

    return {"items": items, "total": total, "currency": group_by != "quantity"}
