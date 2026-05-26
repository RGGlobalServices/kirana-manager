from fastapi import APIRouter, Depends, HTTPException, status, Body, File, UploadFile
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database.database import get_db
from ..models import models
from ..schemas import schemas
from ..repositories.product_repository import ProductRepository
from .deps import get_current_shop
from .ai_utils import extract_product_details
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[schemas.Product])
def get_products(
    db: Session = Depends(get_db), 
    shop: models.Shop = Depends(get_current_shop)
):
    repo = ProductRepository(db, shop.id)
    return repo.get_all()

@router.post("/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    repo = ProductRepository(db, shop.id)
    return repo.create(product)

@router.get("/{barcode}", response_model=schemas.Product)
def get_product_by_barcode(
    barcode: str, 
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    repo = ProductRepository(db, shop.id)
    product = repo.get_by_barcode(barcode)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: UUID,
    updates: dict = Body(...),
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    repo = ProductRepository(db, shop.id)
    product = repo.update(product_id, updates)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    repo = ProductRepository(db, shop.id)
    if not repo.delete(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"ok": True}

@router.post("/{product_id}/adjust")
def adjust_stock(
    product_id: UUID,
    body: dict = Body(...),
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    repo = ProductRepository(db, shop.id)
    # body should have quantity, type, note
    product = repo.adjust_stock(
        product_id, 
        body.get("quantity", 0), 
        body.get("type", "edit"), 
        body.get("note", "")
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/logs/all")
def get_stock_logs(
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    repo = ProductRepository(db, shop.id)
    return repo.get_logs()
