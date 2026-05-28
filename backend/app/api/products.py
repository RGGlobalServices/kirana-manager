from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database.database import get_db
from ..models import models
from ..schemas import schemas
from ..repositories.product_repository import ProductRepository

router = APIRouter()

class AdjustStockRequest(BaseModel):
    quantity: float
    type: str
    note: Optional[str] = None

@router.get("/", response_model=List[schemas.Product])
def get_products(db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    return repo.get_all()

@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    return repo.create(product)

@router.put("/{product_id}")
def update_product(product_id: int, updates: dict, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    product = repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in updates.items():
        if hasattr(product, key):
            setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    product = repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"status": "deleted"}

@router.post("/{product_id}/adjust")
def adjust_stock(product_id: int, req: AdjustStockRequest, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    product = repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if req.type in ("add", "in"):
        product.current_stock += req.quantity
    else:
        product.current_stock = max(0, product.current_stock - req.quantity)

    log = models.StockLog(
        shop_id=product.shop_id,
        product_id=product.id,
        product_name=product.name,
        quantity_change=req.quantity if req.type in ("add", "in") else -req.quantity,
        reason=req.note or f"Stock {req.type}"
    )
    db.add(log)
    db.commit()
    db.refresh(product)
    return product

@router.get("/logs/all")
def get_stock_logs(db: Session = Depends(get_db)):
    logs = db.query(models.StockLog).order_by(models.StockLog.created_at.desc()).limit(100).all()
    return [
        {
            "id": str(log.id),
            "product_name": log.product_name,
            "quantity_change": log.quantity_change,
            "reason": log.reason,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in logs
    ]

@router.get("/{barcode}", response_model=schemas.Product)
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    product = repo.get_by_barcode(barcode)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
