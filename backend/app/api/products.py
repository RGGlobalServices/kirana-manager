from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..models import models
from ..schemas import schemas
from ..repositories.product_repository import ProductRepository

router = APIRouter()

@router.get("/", response_model=List[schemas.Product])
def get_products(db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    return repo.get_all()

@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    return repo.create(product)

@router.get("/{barcode}", response_model=schemas.Product)
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    product = repo.get_by_barcode(barcode)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
