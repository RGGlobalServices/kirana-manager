"""Shop profile API — GET and PATCH the authenticated shop's business type & settings"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models import models
from ..schemas import schemas
from .deps import get_current_shop

router = APIRouter()

@router.get("/profile", response_model=schemas.ShopProfile)
def get_shop_profile(
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    return shop

@router.patch("/profile", response_model=schemas.ShopProfile)
def update_shop_profile(
    updates: schemas.ShopUpdate,
    db: Session = Depends(get_db),
    shop: models.Shop = Depends(get_current_shop)
):
    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(shop, key):
            setattr(shop, key, value)
    db.commit()
    db.refresh(shop)
    return shop
