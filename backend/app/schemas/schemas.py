from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    category: str
    base_unit: str
    mrp: float
    selling_price: float
    wholesale_cost: float
    conversion_factor: float = 1.0
    min_stock: float
    current_stock: float
    barcode: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    shop_id: int

    class Config:
        from_attributes = True

class SaleItemBase(BaseModel):
    product_id: int
    unit: str
    quantity: float
    price_per_unit: float
    margin_per_unit: float

class SaleCreate(BaseModel):
    customer_id: Optional[int] = None
    items: List[SaleItemBase]
    total_amount: float
    total_profit: float
    payment_type: str

class Sale(BaseModel):
    id: int
    total_amount: float
    total_profit: float
    created_at: datetime
    
    class Config:
        from_attributes = True
