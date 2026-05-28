from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database.database import get_db
from ..models import models
from .deps import get_current_shop
from .analytics_utils import get_top_products_data
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    today = datetime.now().date()

    base = db.query(func.sum(models.Sale.total_amount)).filter(models.Sale.shop_id == shop.id)
    today_sales = base.filter(func.date(models.Sale.created_at) == today).scalar() or 0

    base_profit = db.query(func.sum(models.Sale.total_profit)).filter(models.Sale.shop_id == shop.id)
    today_profit = base_profit.filter(func.date(models.Sale.created_at) == today).scalar() or 0

    total_udhar = db.query(func.sum(models.Customer.total_due)).filter(models.Customer.shop_id == shop.id).scalar() or 0

    low_stock = db.query(models.Product).filter(
        models.Product.shop_id == shop.id,
        models.Product.current_stock <= models.Product.min_stock
    ).count()

    return {
        "today_sales": today_sales,
        "today_profit": today_profit,
        "total_udhar": total_udhar,
        "low_stock_count": low_stock
    }

@router.get("/sales-trend")
def get_sales_trend(
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)

    results = db.query(
        func.date(models.Sale.created_at).label('date'),
        func.sum(models.Sale.total_amount).label('total')
    ).filter(
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) >= start_date
    ).group_by(func.date(models.Sale.created_at)).all()

    return [{"date": r.date.strftime("%Y-%m-%d"), "total": r.total} for r in results]

@router.get("/top-products")
def top_products(
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop),
    group_by: str = "revenue",
    limit: int = 10,
    days: int = 30,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    return get_top_products_data(db, shop.id, group_by, limit, days, start_date, end_date)

@router.get("/low-stock")
def low_stock(
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop),
    limit: int = 5
):
    products = db.query(models.Product).filter(
        models.Product.shop_id == shop.id,
        models.Product.current_stock <= models.Product.min_stock
    ).order_by(models.Product.current_stock.asc()).limit(limit).all()

    return [
        {
            "id": str(p.id),
            "name": p.name,
            "category": p.category,
            "current_stock": p.current_stock,
            "min_stock": p.min_stock,
            "unit": p.base_unit,
            "status": "out_of_stock" if p.current_stock <= 0 else "low_stock"
        }
        for p in products
    ]

@router.get("/recent-bills")
def recent_bills(
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    bills = db.query(models.Sale).filter(
        models.Sale.shop_id == shop.id
    ).order_by(models.Sale.created_at.desc()).limit(5).all()

    return [
        {
            "id": str(b.id),
            "total_amount": b.total_amount,
            "payment_type": b.payment_type,
            "created_at": b.created_at.isoformat() if b.created_at else None,
            "customer_name": b.customer.name if b.customer else "Walk-in"
        }
        for b in bills
    ]

@router.get("/ai-context")
def ai_context(
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    today = datetime.now().date()
    products_count = db.query(models.Product).filter(models.Product.shop_id == shop.id).count()
    today_sales = db.query(func.sum(models.Sale.total_amount)).filter(
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) == today
    ).scalar() or 0
    low_stock_items = db.query(models.Product).filter(
        models.Product.shop_id == shop.id,
        models.Product.current_stock <= models.Product.min_stock
    ).count()

    return {
        "shop_name": shop.name,
        "products_count": products_count,
        "today_sales": today_sales,
        "low_stock_items": low_stock_items,
        "subscription_plan": shop.subscription_plan
    }

@router.get("/product-insights/{product_id}")
def product_insights(
    product_id: int,
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.shop_id == shop.id
    ).first()
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")

    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        except ValueError:
            start_dt = datetime.now() - timedelta(days=30)
            end_dt = datetime.now() + timedelta(days=1)
    else:
        start_dt = datetime.now() - timedelta(days=30)
        end_dt = datetime.now() + timedelta(days=1)

    sales_data = db.query(
        func.count(models.SaleItem.id).label("total_sales"),
        func.sum(models.SaleItem.quantity).label("total_qty"),
        func.sum(models.SaleItem.quantity * models.SaleItem.price_per_unit).label("revenue"),
        func.sum(models.SaleItem.quantity * models.SaleItem.margin_per_unit).label("profit")
    ).join(models.Sale).filter(
        models.Sale.shop_id == shop.id,
        models.SaleItem.product_id == product_id,
        models.Sale.created_at >= start_dt,
        models.Sale.created_at < end_dt
    ).first()

    return {
        "id": str(product.id),
        "name": product.name,
        "category": product.category,
        "current_stock": product.current_stock,
        "min_stock": product.min_stock,
        "mrp": product.mrp,
        "selling_price": product.selling_price,
        "total_sales": int(sales_data.total_sales or 0),
        "total_qty": float(sales_data.total_qty or 0),
        "revenue": float(sales_data.revenue or 0),
        "profit": float(sales_data.profit or 0)
    }

@router.get("/business-report")
def business_report(
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    today = datetime.now().date()
    month_start = today.replace(day=1)

    period_sales = db.query(func.sum(models.Sale.total_amount)).filter(
        models.Sale.shop_id == shop.id,
        models.Sale.created_at >= month_start
    ).scalar() or 0

    period_profit = db.query(func.sum(models.Sale.total_profit)).filter(
        models.Sale.shop_id == shop.id,
        models.Sale.created_at >= month_start
    ).scalar() or 0

    period_bills = db.query(func.count(models.Sale.id)).filter(
        models.Sale.shop_id == shop.id,
        models.Sale.created_at >= month_start
    ).scalar() or 0

    total_products = db.query(models.Product).filter(models.Product.shop_id == shop.id).count()
    total_customers = db.query(models.Customer).filter(models.Customer.shop_id == shop.id).count()

    return {
        "shop_name": shop.name,
        "period": "this_month",
        "total_sales": period_sales,
        "total_profit": period_profit,
        "total_bills": period_bills,
        "total_products": total_products,
        "total_customers": total_customers,
        "subscription_plan": shop.subscription_plan
    }

@router.get("/export")
def export_report(
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    today = datetime.now().date()
    month_start = today.replace(day=1)

    sales = db.query(models.Sale).filter(
        models.Sale.shop_id == shop.id,
        models.Sale.created_at >= month_start
    ).order_by(models.Sale.created_at.desc()).all()

    rows = []
    for s in sales:
        rows.append({
            "id": str(s.id),
            "date": s.created_at.isoformat() if s.created_at else "",
            "amount": s.total_amount,
            "profit": s.total_profit,
            "payment": s.payment_type,
            "customer": s.customer.name if s.customer else "Walk-in"
        })

    return {"rows": rows, "total": len(rows), "period": "this_month"}
