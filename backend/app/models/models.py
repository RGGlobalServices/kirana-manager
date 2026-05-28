from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.database import Base
import enum

class BaseUnit(str, enum.Enum):
    KG = "Kg"
    GRAM = "Gram"
    BOTTLE = "Bottle"
    BOX = "Box"
    GONI = "Goni"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    full_name = Column(String, nullable=True)
    mobile = Column(String, nullable=True)
    password = Column(String)
    store_name = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Shop(Base):
    __tablename__ = "shops"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String, index=True)
    address = Column(String, nullable=True)
    mobile = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    setup_complete = Column(Integer, default=0)
    subscription_plan = Column(String, default='starter')
    subscription_status = Column(String, default='active')
    subscription_expiry = Column(DateTime(timezone=True), nullable=True)
    subscription_cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner = relationship("User", backref="shops")
    products = relationship("Product", back_populates="shop")
    sales = relationship("Sale", back_populates="shop")
    customers = relationship("Customer", back_populates="shop")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"))
    name = Column(String, index=True)
    category = Column(String, index=True)
    base_unit = Column(String)
    mrp = Column(Float)
    selling_price = Column(Float)
    wholesale_cost = Column(Float)
    conversion_factor = Column(Float, default=1.0)
    min_stock = Column(Float)
    current_stock = Column(Float)
    barcode = Column(String, index=True, unique=True)
    expiry_date = Column(String, nullable=True)
    shop = relationship("Shop", back_populates="products")

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"))
    name = Column(String, index=True)
    mobile = Column(String, index=True)
    total_due = Column(Float, default=0.0)
    shop = relationship("Shop", back_populates="customers")
    sales = relationship("Sale", back_populates="customer")

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    total_amount = Column(Float)
    total_profit = Column(Float)
    payment_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    shop = relationship("Shop", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale")

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    unit = Column(String)
    quantity = Column(Float)
    price_per_unit = Column(Float)
    margin_per_unit = Column(Float)
    sale = relationship("Sale", back_populates="items")

class StockLog(Base):
    __tablename__ = "stock_logs"
    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id"))
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String, nullable=True)
    quantity_change = Column(Float)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PushSubscription(Base):
    __tablename__ = "push_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    endpoint = Column(String)
    p256dh = Column(String)
    auth = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NotificationSetting(Base):
    __tablename__ = "notification_settings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    daily_summary_enabled = Column(Boolean, default=True)
    low_stock_alert_enabled = Column(Boolean, default=True)
    alert_time = Column(String, nullable=True)

class UserNotification(Base):
    __tablename__ = "user_notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    admin_notification_id = Column(Integer, ForeignKey("admin_notifications.id"), nullable=True)
    title = Column(String)
    message = Column(Text)
    notification_type = Column(String)
    is_read = Column(Boolean, default=False)
    link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdminNotification(Base):
    __tablename__ = "admin_notifications"
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"))
    title = Column(String)
    message = Column(Text)
    notification_type = Column(String)
    target_audience = Column(String)
    target_plan = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ReferralCode(Base):
    __tablename__ = "referral_codes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    code = Column(String, unique=True, index=True)
    total_referrals = Column(Integer, default=0)
    successful_referrals = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Referral(Base):
    __tablename__ = "referrals"
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referred_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    referred_email = Column(String, nullable=True)
    referral_code = Column(String)
    status = Column(String, default='pending')
    discount_applied = Column(Boolean, default=False)
    referrer_rewarded = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id = Column(Integer, primary_key=True, index=True)
    display_id = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String, nullable=True)
    shop_name = Column(String, nullable=True)
    type = Column(String)
    priority = Column(String, default='normal')
    subject = Column(String, nullable=True)
    message = Column(Text)
    status = Column(String, default='open')
    admin_notes = Column(Text, nullable=True)
    refund_amount = Column(String, nullable=True)
    refund_reason = Column(String, nullable=True)
    txn_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

class DukandarRelationship(Base):
    __tablename__ = "dukandar_relationships"
    id = Column(Integer, primary_key=True, index=True)
    wholesaler_id = Column(Integer, ForeignKey("users.id"))
    retailer_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default='admin')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
