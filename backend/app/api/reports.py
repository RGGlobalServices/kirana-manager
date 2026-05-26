from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database.database import get_db
from ..models import models
from .deps import get_current_shop
from datetime import datetime, timedelta
from .analytics_utils import get_top_products_data
from ..schemas import schemas

router = APIRouter()

@router.get("/top-products")
def get_top_products(
    group_by: str = Query("revenue", description="revenue | quantity | category | udhar"),
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    return get_top_products_data(db, shop.id, group_by=group_by, limit=limit, days=days, start_date=start_date, end_date=end_date)


@router.get("/summary")
def get_summary(
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db), 
    shop: models.Shop = Depends(get_current_shop)
):
    # Use the strings directly for date comparison to be robust across DBs (SQLite/Postgres)
    # If not provided, use today's date in YYYY-MM-DD format
    s_date = start_date if start_date else datetime.now().strftime("%Y-%m-%d")
    e_date = end_date if end_date else datetime.now().strftime("%Y-%m-%d")

    today_sales = db.query(func.sum(models.Sale.total_amount)).filter(
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) >= s_date,
        func.date(models.Sale.created_at) <= e_date
    ).scalar() or 0
    today_profit = db.query(func.sum(models.Sale.total_profit)).filter(
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) >= s_date,
        func.date(models.Sale.created_at) <= e_date
    ).scalar() or 0
    total_udhar = db.query(func.sum(models.Customer.total_due)).filter(
        models.Customer.shop_id == shop.id
    ).scalar() or 0
    low_stock_count = db.query(models.Product).filter(
        models.Product.shop_id == shop.id,
        models.Product.current_stock <= models.Product.min_stock
    ).count()

    return {
        "today_sales": today_sales,
        "today_profit": today_profit,
        "total_udhar": total_udhar,
        "low_stock_count": low_stock_count
    }

@router.get("/sales-trend")
def get_sales_trend(db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    # Last 7 days
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

@router.get("/top-udhar", response_model=List[schemas.Customer])
def get_top_udhar(db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    return db.query(models.Customer).filter(
        models.Customer.shop_id == shop.id,
        models.Customer.total_due > 0
    ).order_by(models.Customer.total_due.desc()).limit(5).all()

@router.get("/low-stock", response_model=List[schemas.Product])
def get_low_stock(
    limit: int = 5,
    db: Session = Depends(get_db), 
    shop: models.Shop = Depends(get_current_shop)
):
    return db.query(models.Product).filter(
        models.Product.shop_id == shop.id,
        models.Product.current_stock <= models.Product.min_stock
    ).limit(limit).all()

@router.get("/recent-sales-items")
def get_recent_sales_items(db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    # Get last 5 items sold
    results = db.query(
        models.SaleItem, 
        models.Product.name,
        models.Sale.created_at
    ).join(models.Sale).join(models.Product).filter(
        models.Sale.shop_id == shop.id
    ).order_by(models.Sale.created_at.desc()).limit(5).all()
    
    return [
        {
            "name": r.name,
            "qty": r.SaleItem.quantity,
            "amount": r.SaleItem.quantity * r.SaleItem.price_per_unit,
            "created_at": r.created_at
        } for r in results
    ]

@router.get("/recent-bills", response_model=List[schemas.Sale])
def get_recent_bills(db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    # Using Sale model as 'Bills'
    results = db.query(models.Sale).filter(
        models.Sale.shop_id == shop.id
    ).order_by(models.Sale.created_at.desc()).limit(5).all()
    
    # We might need to join or count items
    return results

@router.get("/category-distribution")
def get_category_distribution(db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    results = db.query(
        models.Product.category,
        func.count(models.Product.id).label('count')
    ).filter(
        models.Product.shop_id == shop.id
    ).group_by(models.Product.category).all()
    
    return [{"name": r.category, "value": r.count} for r in results]


@router.get("/business-report")
def get_business_report(db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    # 1. Sales vs Profit Trend (Last 7 Days)
    days = []
    trend_data = []
    for i in range(6, -1, -1):
        dt = datetime.now() - timedelta(days=i)
        days.append(dt.date())
    
    for d in days:
        sales = db.query(func.sum(models.Sale.total_amount)).filter(
            models.Sale.shop_id == shop.id,
            func.date(models.Sale.created_at) == d
        ).scalar() or 0
        profit = db.query(func.sum(models.Sale.total_profit)).filter(
            models.Sale.shop_id == shop.id,
            func.date(models.Sale.created_at) == d
        ).scalar() or 0
        trend_data.append({
            "name": d.strftime("%a"),
            "fullDate": d.strftime("%Y-%m-%d"),
            "sales": float(sales),
            "profit": float(profit)
        })

    # 2. Top Selling Products
    top_products_query = db.query(
        models.Product.name,
        func.sum(models.SaleItem.quantity * models.SaleItem.price_per_unit).label('revenue')
    ).join(models.SaleItem).join(models.Sale).filter(
        models.Sale.shop_id == shop.id
    ).group_by(models.Product.name).order_by(func.sum(models.SaleItem.quantity * models.SaleItem.price_per_unit).desc()).limit(5).all()

    top_products = [
        {"name": r.name, "revenue": float(r.revenue), "growth": "+0%"} # Growth is mocked for now
        for r in top_products_query
    ]

    # 3. Category Performance
    cat_query = db.query(
        models.Product.category,
        func.count(models.SaleItem.id).label('count')
    ).join(models.SaleItem).join(models.Sale).filter(
        models.Sale.shop_id == shop.id
    ).group_by(models.Product.category).all()
    
    total_items = sum(r.count for r in cat_query) or 1
    cat_performance = [
        {"name": r.category, "percentage": round((r.count / total_items) * 100)}
        for r in cat_query
    ]

    return {
        "trend": trend_data,
        "topProducts": top_products,
        "categories": cat_performance
    }

@router.get("/milestones")
def get_milestones(db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    today = datetime.now().date()
    memories = []
    
    # 1. Exactly 1 Year Ago
    one_year_ago = today - timedelta(days=365)
    year_sales = db.query(func.sum(models.Sale.total_amount)).filter(
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) == one_year_ago
    ).scalar() or 0
    if year_sales > 0:
        memories.append({
            "title": "1 Year ago today",
            "date": one_year_ago.strftime("%d %b %Y"),
            "value": f"₹{year_sales:,.0f}",
            "description": f"You made ₹{year_sales:,.0f} in sales. How much have you grown since then?",
            "type": "year"
        })
        
    # 2. Exactly 6 Months Ago
    six_months_ago = today - timedelta(days=180)
    month_sales = db.query(func.sum(models.Sale.total_amount)).filter(
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) == six_months_ago
    ).scalar() or 0
    if month_sales > 0:
        memories.append({
            "title": "6 Months flashback",
            "date": six_months_ago.strftime("%d %b %Y"),
            "value": f"₹{month_sales:,.0f}",
            "description": f"Your store was busy 6 months ago! Remember this day?",
            "type": "month"
        })

    # 3. High Sales Record
    max_sale = db.query(func.max(models.Sale.total_amount)).filter(
        models.Sale.shop_id == shop.id
    ).scalar() or 0
    if max_sale > 0:
        memories.append({
            "title": "Personal Best",
            "date": "All-time",
            "value": f"₹{max_sale:,.0f}",
            "description": "Your highest ever single bill. Can you beat this today?",
            "type": "record"
        })

    return memories

@router.get("/ai-context")
def get_ai_context(db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    yesterday = (datetime.now() - timedelta(days=1)).date()
    
    # Yesterday's Stats
    yesterday_sales = db.query(func.sum(models.Sale.total_amount)).filter(
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) == yesterday
    ).scalar() or 0
    yesterday_profit = db.query(func.sum(models.Sale.total_profit)).filter(
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) == yesterday
    ).scalar() or 0
    yesterday_count = db.query(models.Sale).filter(
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) == yesterday
    ).count()

    # Yesterday's items for "Top selling"
    top_selling = db.query(
        models.Product.name,
        func.sum(models.SaleItem.quantity).label('qty')
    ).join(models.SaleItem).join(models.Sale).filter(
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) == yesterday
    ).group_by(models.Product.name).order_by(func.sum(models.SaleItem.quantity).desc()).limit(3).all()

    # All Products (for comprehensive analysis)
    products = db.query(models.Product).filter(models.Product.shop_id == shop.id).all()
    
    return {
        "summary": {
            "sales": yesterday_sales,
            "profit": yesterday_profit,
            "cost": yesterday_sales - yesterday_profit,
            "transactions": yesterday_count,
            "top_selling": [{"name": r.name, "qty": r.qty} for r in top_selling]
        },
        "products": [
            {
                "name": p.name,
                "category": p.category,
                "stock": p.current_stock,
                "minStock": p.min_stock,
                "mrp": p.mrp,
                "sellingPrice": p.selling_price,
                "cost": p.wholesale_cost
            } for p in products
        ]
    }

@router.get("/export")
def export_business_data(db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    import csv
    import io
    from fastapi.responses import StreamingResponse

    output = io.StringIO()
    writer = csv.writer(output)

    # 1. Sales Report
    writer.writerow(["--- SALES REPORT ---"])
    writer.writerow(["Date", "Bill No", "Customer", "Total Amount", "Profit", "Payment"])
    sales = db.query(models.Sale).filter(models.Sale.shop_id == shop.id).order_by(models.Sale.created_at.desc()).all()
    for s in sales:
        writer.writerow([s.created_at.strftime("%Y-%m-%d %H:%M"), s.id, "Walk-in", s.total_amount, s.total_profit, "Cash"])
    
    writer.writerow([])
    writer.writerow([])

    # 2. Stock Report
    writer.writerow(["--- STOCK REPORT ---"])
    writer.writerow(["Product Name", "Category", "Current Stock", "Min Stock", "Unit", "MRP", "Selling Price", "Cost"])
    products = db.query(models.Product).filter(models.Product.shop_id == shop.id).all()
    for p in products:
        writer.writerow([p.name, p.category, p.current_stock, p.min_stock, p.base_unit, p.mrp, p.selling_price, p.wholesale_cost])

    writer.writerow([])
    writer.writerow([])
    
    # 3. Customer Ledger
    writer.writerow(["--- CUSTOMER LEDGER (UDHAR) ---"])
    writer.writerow(["Customer Name", "Contact", "Total Due"])
    customers = db.query(models.Customer).filter(models.Customer.shop_id == shop.id).all()
    for c in customers:
        writer.writerow([c.name, c.mobile or "N/A", c.total_due])

    output.seek(0)
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=business_report_{datetime.now().strftime('%Y%m%d')}.csv"
    return response

@router.get("/product-insights/{product_id}")
def get_product_insights(
    product_id: str,
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db), 
    shop: models.Shop = Depends(get_current_shop)
):
    from fastapi import HTTPException
    
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.shop_id == shop.id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            start_dt = datetime.now().date() - timedelta(days=30)
            end_dt = datetime.now().date()
    else:
        start_dt = datetime.now().date() - timedelta(days=30)
        end_dt = datetime.now().date()

    # Get overall stats for timeframe
    stats = db.query(
        func.sum(models.SaleItem.quantity).label("total_qty"),
        func.sum(models.SaleItem.quantity * models.SaleItem.price_per_unit).label("total_revenue"),
        func.sum(models.SaleItem.quantity * models.SaleItem.margin_per_unit).label("total_profit")
    ).join(models.Sale).filter(
        models.SaleItem.product_id == product.id,
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) >= start_dt,
        func.date(models.Sale.created_at) <= end_dt
    ).first()

    # Get daily trend
    trend_results = db.query(
        func.date(models.Sale.created_at).label('date'),
        func.sum(models.SaleItem.quantity).label('qty'),
        func.sum(models.SaleItem.quantity * models.SaleItem.price_per_unit).label('revenue')
    ).join(models.Sale).filter(
        models.SaleItem.product_id == product.id,
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) >= start_dt,
        func.date(models.Sale.created_at) <= end_dt
    ).group_by(func.date(models.Sale.created_at)).order_by(func.date(models.Sale.created_at)).all()

    # Get recent transactions
    recent_sales = db.query(
        models.Sale.created_at,
        models.SaleItem.quantity,
        models.SaleItem.price_per_unit,
        (models.SaleItem.quantity * models.SaleItem.price_per_unit).label('total')
    ).join(models.Sale).filter(
        models.SaleItem.product_id == product.id,
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) >= start_dt,
        func.date(models.Sale.created_at) <= end_dt
    ).order_by(models.Sale.created_at.desc()).limit(10).all()

    return {
        "product": {
            "id": str(product.id),
            "name": product.name,
            "category": product.category,
            "stock": product.current_stock,
            "minStock": product.min_stock,
            "price": product.selling_price,
            "cost": product.wholesale_cost,
            "unit": product.base_unit
        },
        "stats": {
            "unitsSold": float(stats.total_qty or 0),
            "revenue": float(stats.total_revenue or 0),
            "profit": float(stats.total_profit or 0)
        },
        "trend": [
            {
                "date": r.date.strftime("%Y-%m-%d"),
                "qty": float(r.qty or 0),
                "revenue": float(r.revenue or 0)
            } for r in trend_results
        ],
        "recentSales": [
            {
                "date": r.created_at.strftime("%Y-%m-%d %H:%M"),
                "qty": float(r.quantity),
                "price": float(r.price_per_unit),
                "total": float(r.total)
            } for r in recent_sales
        ]
    }
