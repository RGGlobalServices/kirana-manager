from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..schemas import schemas
from ..models import models

router = APIRouter()

@router.post("/", response_model=schemas.Sale)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    # Start transaction
    db_sale = models.Sale(
        customer_id=sale.customer_id,
        total_amount=sale.total_amount,
        total_profit=sale.total_profit,
        payment_type=sale.payment_type,
        shop_id=1 # Hardcoded for demo
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

    # Update Udhar if applicable
    if sale.payment_type == "Udhar" and sale.customer_id:
        customer = db.query(models.Customer).filter(models.Customer.id == sale.customer_id).first()
        if customer:
            customer.total_due += sale.total_amount

    db.commit()
    db.refresh(db_sale)
    return db_sale
