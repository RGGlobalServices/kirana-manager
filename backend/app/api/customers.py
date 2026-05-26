from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from ..database.database import get_db
from ..models import models
from .deps import get_current_shop
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

router = APIRouter()

class CustomerCreate(BaseModel):
    name: str
    mobile: str

class TransactionCreate(BaseModel):
    type: str # udhar, payment
    amount: float
    note: Optional[str] = ""
    date: Optional[str] = None
    billNumber: Optional[str] = None

@router.get("/")
def get_customers(db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    return db.query(models.Customer).filter(models.Customer.shop_id == shop.id).options(joinedload(models.Customer.transactions)).all()

@router.post("/")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    db_customer = models.Customer(name=customer.name, mobile=customer.mobile, shop_id=shop.id)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.put("/{customer_id}")
def update_customer(customer_id: UUID, customer: CustomerCreate, db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id, models.Customer.shop_id == shop.id).first()
    if not db_customer: raise HTTPException(status_code=404)
    db_customer.name = customer.name
    db_customer.mobile = customer.mobile
    db.commit()
    return db_customer

@router.delete("/{customer_id}")
def delete_customer(customer_id: UUID, db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id, models.Customer.shop_id == shop.id).first()
    if not db_customer: raise HTTPException(status_code=404)
    db.delete(db_customer)
    db.commit()
    return {"ok": True}

@router.post("/{customer_id}/transactions")
def add_transaction(customer_id: UUID, tx: TransactionCreate, db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id, models.Customer.shop_id == shop.id).first()
    if not customer: raise HTTPException(status_code=404)
    
    db_tx = models.CustomerTransaction(
        customer_id=customer_id,
        type=tx.type,
        amount=tx.amount,
        note=tx.note,
        bill_number=tx.billNumber
    )
    db.add(db_tx)
    
    if tx.type == "udhar": customer.total_due += tx.amount
    else: customer.total_due -= tx.amount
    
    db.commit()
    return db_tx

@router.delete("/{customer_id}/transactions/{tx_id}")
def delete_transaction(customer_id: UUID, tx_id: UUID, db: Session = Depends(get_db), shop: models.Shop = Depends(get_current_shop)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id, models.Customer.shop_id == shop.id).first()
    if not customer: raise HTTPException(status_code=404)
    
    tx = db.query(models.CustomerTransaction).filter(models.CustomerTransaction.id == tx_id, models.CustomerTransaction.customer_id == customer_id).first()
    if not tx: raise HTTPException(status_code=404)
    
    if tx.type == "udhar": customer.total_due -= tx.amount
    else: customer.total_due += tx.amount
    
    db.delete(tx)
    db.commit()
    return {"ok": True}
