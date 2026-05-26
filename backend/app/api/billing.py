from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, String
from datetime import datetime
from ..database.database import get_db
from ..schemas import schemas
from ..models import models

from .deps import get_current_shop

router = APIRouter()

@router.post("/", response_model=schemas.Sale)
def create_sale(
    sale: schemas.SaleCreate, 
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    # Generate Invoice Number: INVC-YYYYMMDD-SEQUENCE
    today = datetime.now().date()
    today_str = today.strftime("%Y%m%d")
    
    # Count sales today for this shop to get sequence
    count_today = db.query(models.Sale).filter(
        models.Sale.shop_id == shop.id,
        func.date(models.Sale.created_at) == today
    ).count()
    
    invoice_num = f"INVC-{today_str}-{count_today + 1}"

    # Start transaction
    db_sale = models.Sale(
        customer_id=sale.customer_id,
        invoice_number=invoice_num,
        total_amount=sale.total_amount,
        total_profit=sale.total_profit,
        payment_type=sale.payment_type,
        shop_id=shop.id
    )
    db.add(db_sale)
    db.flush()

    for item in sale.items:
        db_item = models.SaleItem(
            sale_id=db_sale.id,
            product_id=item.product_id,
            unit=item.unit,
            quantity=item.quantity,
            price_per_unit=item.price_per_unit,
            margin_per_unit=item.margin_per_unit
        )
        db.add(db_item)
        
        # Update stock
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.current_stock -= item.quantity
            # Record stock movement
            db_log = models.StockLog(
                shop_id=shop.id,
                product_id=item.product_id,
                type="out",
                quantity=item.quantity,
                note=f"Sold in Sale #{str(db_sale.id)[:8]}"
            )
            db.add(db_log)

    # Note: Udhar/Credit is handled by the frontend calling the customers API directly
    # to support split payments and proper customer management.

    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.get("/", response_model=list[schemas.Sale])
def get_sales(
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    return db.query(models.Sale).filter(
        models.Sale.shop_id == shop.id
    ).order_by(models.Sale.created_at.desc()).all()

@router.get("/{sale_id}")
def get_sale_detail(
    sale_id: str,
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    # Try to find by UUID first (legacy/internal)
    sale = None
    try:
        import uuid
        # Clean potential prefix if user typed it
        clean_id = sale_id.upper().replace("INV-", "").replace("INVC-", "")
        print(f"DEBUG: Searching for invoice: {sale_id}, cleaned: {clean_id}")
        target_uuid = uuid.UUID(clean_id)
        sale = db.query(models.Sale).filter(
            models.Sale.id == target_uuid,
            models.Sale.shop_id == shop.id
        ).first()
    except (ValueError, AttributeError):
        pass # Not a UUID
    
    # If not found by exact UUID, try smarter searching
    if not sale:
        # 1. Try to find by invoice_number exact match
        sale = db.query(models.Sale).filter(
            models.Sale.invoice_number == sale_id,
            models.Sale.shop_id == shop.id
        ).first()
        
        # 2. Try to find by ID prefix (the short ID shown in UI)
        if not sale and clean_id:
            sale = db.query(models.Sale).filter(
                func.cast(models.Sale.id, String).ilike(f"{clean_id}%"),
                models.Sale.shop_id == shop.id
            ).first()
            
        # 3. Try to find by invoice_number containing the string
        if not sale and clean_id:
             sale = db.query(models.Sale).filter(
                models.Sale.invoice_number.ilike(f"%{clean_id}%"),
                models.Sale.shop_id == shop.id
            ).first()

    if not sale:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    # Join with items and product names
    items = db.query(
        models.SaleItem,
        models.Product.name,
        models.Product.id.label("product_id")
    ).outerjoin(models.Product).filter(
        models.SaleItem.sale_id == sale.id
    ).all()
    
    result_items = []
    for item, product_name, product_id in items:
        result_items.append({
            "id": str(item.id),
            "product_id": str(product_id) if product_id else None,
            "name": product_name or "Custom Item",
            "unit": item.unit,
            "quantity": item.quantity,
            "price_per_unit": item.price_per_unit,
            "total": item.quantity * item.price_per_unit
        })
        
    return {
        "id": str(sale.id),
        "invoice_number": sale.invoice_number,
        "total_amount": sale.total_amount,
        "payment_type": sale.payment_type,
        "created_at": sale.created_at,
        "customer_name": sale.customer.name if sale.customer else "Walk-in",
        "items": result_items
    }

@router.post("/returns")
def process_return(
    return_in: schemas.ReturnCreate,
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    sale = db.query(models.Sale).filter(
        models.Sale.id == return_in.bill_id,
        models.Sale.shop_id == shop.id
    ).first()
    
    if not sale:
        raise HTTPException(status_code=404, detail="Original invoice not found")
        
    for item_data in return_in.items:
        sale_item = db.query(models.SaleItem).filter(
            models.SaleItem.id == item_data.item_id,
            models.SaleItem.sale_id == sale.id
        ).first()
        
        if not sale_item: continue
        
        # 1. Update stock (return adds back to stock)
        if sale_item.product_id:
            product = db.query(models.Product).filter(models.Product.id == sale_item.product_id).first()
            if product:
                product.current_stock += item_data.quantity
                # 2. Record stock movement
                db_log = models.StockLog(
                    shop_id=shop.id,
                    product_id=product.id,
                    type="in",
                    quantity=item_data.quantity,
                    note=f"Returned from Invoice #{str(sale.id)[:8]}"
                )
                db.add(db_log)
        
        # 3. Adjust sale totals (optional, but good for reporting)
        # Note: In a real POS, we'd create a separate 'Return' transaction.
        # For now, we'll just adjust the sale amount if we want.
        # But let's just keep it simple and record the stock change.
        
    db.commit()
    return {"status": "success", "message": "Return processed and stock adjusted"}
