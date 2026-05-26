from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[dict] = None

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    shop_name: str # Special field to create a shop on register
    business_type: str = "kirana"
    paid_plan: Optional[str] = None
    paid_txnid: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    password: str

class User(UserBase):
    id: UUID
    is_active: int
    class Config:
        from_attributes = True

# ─── Shop Schemas ──────────────────────────────────────────────────────────────

class ShopProfile(BaseModel):
    id: UUID
    name: str
    address: Optional[str] = None
    mobile: Optional[str] = None
    logo_url: Optional[str] = None
    business_type: str = "kirana"
    setup_complete: bool = False
    subscription_plan: str = "starter"
    subscription_status: str = "active"
    subscription_expiry: Optional[datetime] = None
    class Config:
        from_attributes = True

class ShopUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    mobile: Optional[str] = None
    logo_url: Optional[str] = None
    business_type: Optional[str] = None
    setup_complete: Optional[bool] = None

# ─── Product Schemas ───────────────────────────────────────────────────────────

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
    archived: Optional[bool] = False
    # Business-type-aware extended fields
    expiry_date: Optional[str] = None       # YYYY-MM-DD
    batch_number: Optional[str] = None
    drug_schedule: Optional[str] = None     # OTC / Rx / H1 / H2
    model_number: Optional[str] = None
    warranty_months: Optional[int] = None
    gender: Optional[str] = None            # M / F / Kids / Unisex
    shade: Optional[str] = None
    size_variants: Optional[str] = None     # JSON string: {"S":10,"M":25}
    is_loose: Optional[bool] = False

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: UUID
    shop_id: UUID
    is_loose: bool = False

    class Config:
        from_attributes = True

class SaleItemBase(BaseModel):
    product_id: Optional[UUID] = None
    unit: str
    quantity: float
    price_per_unit: float
    margin_per_unit: float

class SaleCreate(BaseModel):
    customer_id: Optional[UUID] = None
    items: List[SaleItemBase]
    total_amount: float
    total_profit: float
    payment_type: str

class Sale(BaseModel):
    id: UUID
    invoice_number: Optional[str] = None
    total_amount: float
    total_profit: float
    payment_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Customer(BaseModel):
    id: UUID
    name: str
    mobile: Optional[str] = None
    total_due: float = 0.0
    
    class Config:
        from_attributes = True

class ReturnItem(BaseModel):
    item_id: UUID
    quantity: float

class ReturnCreate(BaseModel):
    bill_id: UUID
    items: List[ReturnItem]

class GoogleAuthRequest(BaseModel):
    credential: str
