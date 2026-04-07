from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models import models

router = APIRouter()

@router.get("/")
def get_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()

@router.get("/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()
