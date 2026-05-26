from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
import random
from ..database.database import get_db
from ..models import models
from .deps import get_current_user

router = APIRouter()

class AddDukandarRequest(BaseModel):
    retailer_email: str

class AddDukandarByCodeRequest(BaseModel):
    access_code: str

def _generate_dukandar_access_code(name_base: str) -> str:
    clean = ''.join(c for c in name_base.upper() if c.isalnum() or c == ' ')
    parts = clean.split()
    base = parts[0][:5] if parts else clean[:5]
    if len(base) < 3:
        base = (base + "DUK")[:5]
    suffix = random.randint(10, 999)
    return f"{base}{suffix}"

def _ensure_access_code(db: Session, user: models.User) -> models.ReferralCode:
    code_info = db.query(models.ReferralCode).filter(
        models.ReferralCode.user_id == user.id
    ).first()
    if code_info:
        return code_info

    shop = db.query(models.Shop).filter(models.Shop.owner_id == user.id).first()
    name_for_code = shop.name if shop else user.full_name
    code = _generate_dukandar_access_code(name_for_code)
    for _ in range(20):
        existing = db.query(models.ReferralCode).filter(
            models.ReferralCode.code == code
        ).first()
        if not existing:
            break
        suffix = random.randint(10, 999)
        base = ''.join(c for c in code if not c.isdigit())[:5]
        code = f"{base}{suffix}"

    code_info = models.ReferralCode(user_id=user.id, code=code)
    db.add(code_info)
    db.commit()
    db.refresh(code_info)
    return code_info

@router.get("/my-access-code")
def get_my_access_code(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    code_info = _ensure_access_code(db, user)
    shop = db.query(models.Shop).filter(models.Shop.owner_id == user.id).first()
    return {
        "access_code": code_info.code,
        "shop_name": shop.name if shop else "My Shop",
        "owner_name": user.full_name
    }

@router.post("/add-dukandar")
def add_dukandar(
    req: AddDukandarRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    shop = db.query(models.Shop).filter(models.Shop.owner_id == user.id).first()
    if not shop or shop.subscription_plan != "business":
        raise HTTPException(status_code=403, detail="Only Wholesale plan users can add dukandar")

    retailer = db.query(models.User).filter(models.User.email == req.retailer_email).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found. They must register first.")

    existing = db.query(models.DukandarRelationship).filter(
        models.DukandarRelationship.wholesaler_id == user.id,
        models.DukandarRelationship.retailer_id == retailer.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Dukandar already added")

    relationship = models.DukandarRelationship(
        wholesaler_id=user.id,
        retailer_id=retailer.id
    )
    db.add(relationship)
    db.commit()
    return {"status": "success", "message": "Dukandar added successfully"}

@router.post("/add-dukandar-by-code")
def add_dukandar_by_code(
    req: AddDukandarByCodeRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    shop = db.query(models.Shop).filter(models.Shop.owner_id == user.id).first()
    if not shop or shop.subscription_plan != "business":
        raise HTTPException(status_code=403, detail="Only Wholesale plan users can add dukandar")

    code_upper = req.access_code.upper().strip()
    if not code_upper:
        raise HTTPException(status_code=400, detail="Access code is required")

    code_info = db.query(models.ReferralCode).filter(
        models.ReferralCode.code == code_upper
    ).first()
    if not code_info:
        raise HTTPException(status_code=404, detail="Invalid dukandar access code")

    retailer = db.query(models.User).filter(models.User.id == code_info.user_id).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Dukandar user not found")
    if retailer.id == user.id:
        raise HTTPException(status_code=400, detail="You cannot add yourself as dukandar")

    existing = db.query(models.DukandarRelationship).filter(
        models.DukandarRelationship.wholesaler_id == user.id,
        models.DukandarRelationship.retailer_id == retailer.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Dukandar already added")

    relationship = models.DukandarRelationship(
        wholesaler_id=user.id,
        retailer_id=retailer.id
    )
    db.add(relationship)
    db.commit()
    return {"status": "success", "message": "Dukandar added successfully using access code"}

@router.get("/my-dukandar")
def get_my_dukandar(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    shop = db.query(models.Shop).filter(models.Shop.owner_id == user.id).first()
    if not shop or shop.subscription_plan != "business":
        raise HTTPException(status_code=403, detail="Only Wholesale plan users can view dukandar")

    relations = db.query(models.DukandarRelationship).filter(
        models.DukandarRelationship.wholesaler_id == user.id,
        models.DukandarRelationship.status == "active"
    ).all()

    dukandar_list = []
    for rel in relations:
        retailer_user = db.query(models.User).filter(models.User.id == rel.retailer_id).first()
        retailer_shop = db.query(models.Shop).filter(
            models.Shop.owner_id == rel.retailer_id
        ).first()

        products = db.query(models.Product).filter(
            models.Product.shop_id == retailer_shop.id
        ).all() if retailer_shop else []

        low_stock = [p for p in products if p.current_stock <= p.min_stock]
        expired = [p for p in products if p.expiry_date and p.expiry_date < "2026-01-01"]
        out_of_stock = [p for p in products if p.current_stock <= 0]

        dukandar_list.append({
            "id": str(rel.id),
            "retailer_id": str(rel.retailer_id),
            "retailer_name": retailer_user.full_name if retailer_user else "Unknown",
            "retailer_shop": retailer_shop.name if retailer_shop else "N/A",
            "retailer_email": retailer_user.email if retailer_user else "N/A",
            "subscription_plan": retailer_shop.subscription_plan if retailer_shop else "N/A",
            "subscription_status": retailer_shop.subscription_status if retailer_shop else "N/A",
            "subscription_expiry": retailer_shop.subscription_expiry.isoformat() if retailer_shop and retailer_shop.subscription_expiry else None,
            "stock_alerts": {
                "low_stock": [
                    {"name": p.name, "current": p.current_stock, "min": p.min_stock}
                    for p in low_stock[:10]
                ],
                "out_of_stock": [
                    {"name": p.name} for p in out_of_stock[:10]
                ],
                "expiring_soon": [
                    {"name": p.name, "expiry": p.expiry_date}
                    for p in expired[:10]
                ]
            },
            "total_products": len(products),
            "created_at": rel.created_at.isoformat() if rel.created_at else None
        })

    return {"dukandar": dukandar_list}
