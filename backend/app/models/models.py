from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from ..database.database import Base
import enum
import uuid

class BaseUnit(str, enum.Enum):
    KG = "Kg"
    GRAM = "Gram"
    BOTTLE = "Bottle"
    BOX = "Box"
    GONI = "Goni"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Integer, default=1)
    shops = relationship("Shop", back_populates="owner")

class Shop(Base):
    __tablename__ = "shops"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String, index=True)
    address = Column(String)
    mobile = Column(String)
    logo_url = Column(String)
    business_type = Column(String, default="kirana")
    setup_complete = Column(Boolean, default=False)
    
    # Subscription fields
    subscription_plan        = Column(String,   default="starter")   # starter, basic, professional, business
    subscription_status      = Column(String,   default="active")    # active, trialing, cancelled, expired
    subscription_expiry      = Column(DateTime(timezone=True), nullable=True)
    subscription_cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason      = Column(String,   nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner = relationship("User", back_populates="shops")
    products = relationship("Product", back_populates="shop")
    sales = relationship("Sale", back_populates="shop")
    customers = relationship("Customer", back_populates="shop")

class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"))
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
    archived = Column(Boolean, default=False)
    is_loose = Column(Boolean, default=False)
    # Business-type-aware extended fields
    expiry_date = Column(String, nullable=True)       # YYYY-MM-DD (medical/kirana/cosmetics)
    batch_number = Column(String, nullable=True)      # Medical/pharma batch
    drug_schedule = Column(String, nullable=True)     # OTC / Rx / H1 / H2
    model_number = Column(String, nullable=True)      # Electronics
    warranty_months = Column(Integer, nullable=True)  # Electronics warranty in months
    gender = Column(String, nullable=True)            # M / F / Kids / Unisex (shoes/clothes)
    shade = Column(String, nullable=True)             # Cosmetics shade / color
    size_variants = Column(String, nullable=True)     # JSON: {"S":10,"M":25,"L":5}
    shop = relationship("Shop", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")

class Customer(Base):
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"))
    name = Column(String, index=True)
    mobile = Column(String, index=True)
    total_due = Column(Float, default=0.0)
    shop = relationship("Shop", back_populates="customers")
    sales = relationship("Sale", back_populates="customer")
    transactions = relationship("CustomerTransaction", back_populates="customer")

class CustomerTransaction(Base):
    __tablename__ = "customer_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    type = Column(String) # udhar, payment
    amount = Column(Float)
    note = Column(String)
    bill_number = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    customer = relationship("Customer", back_populates="transactions")

class Sale(Base):
    __tablename__ = "sales"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"))
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    invoice_number = Column(String, unique=True, index=True)
    total_amount = Column(Float)
    total_profit = Column(Float)
    payment_type = Column(String) # Cash, UPI, Udhar
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    shop = relationship("Shop", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale")

class StockLog(Base):
    __tablename__ = "stock_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    type = Column(String) # in, out, edit
    quantity = Column(Float)
    note = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    shop = relationship("Shop")
    product = relationship("Product")

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    unit = Column(String)
    quantity = Column(Float)
    price_per_unit = Column(Float)
    margin_per_unit = Column(Float)
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")

class PushSubscription(Base):
    __tablename__ = "push_subscriptions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    endpoint = Column(String, unique=True, index=True)
    p256dh = Column(String)
    auth = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NotificationSetting(Base):
    __tablename__ = "notification_settings"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    daily_summary_enabled = Column(Boolean, default=True)
    low_stock_alert_enabled = Column(Boolean, default=True)
    alert_time = Column(String, default="08:00") # morning time

# ─── Referral System ──────────────────────────────────────────────────────────────

class Referral(Base):
    __tablename__ = "referrals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # The user who shared their code
    referred_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)   # The user who signed up using the code
    referral_code = Column(String, index=True, nullable=False)                         # The unique code shared
    referred_email = Column(String, nullable=True)                                     # Email of the invited person
    status = Column(String, default="pending")                                         # pending, completed, expired
    discount_applied = Column(Boolean, default=False)                                  # Whether referred user got 20% off
    referrer_rewarded = Column(Boolean, default=False)                                 # Whether referrer got 1 month free
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    referrer = relationship("User", foreign_keys=[referrer_id], backref="referrals_made")
    referred = relationship("User", foreign_keys=[referred_id], backref="referrals_received")

class ReferralCode(Base):
    __tablename__ = "referral_codes"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    code = Column(String, unique=True, index=True, nullable=False)
    total_referrals = Column(Integer, default=0)
    successful_referrals = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="referral_code_info")

# ─── Dukandar (Wholesaler → Retailer) System ─────────────────────────────────────

class DukandarRelationship(Base):
    __tablename__ = "dukandar_relationships"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wholesaler_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # Wholesaler user
    retailer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)    # Dukandar/retailer user
    status = Column(String, default="active")                                            # active, inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    wholesaler = relationship("User", foreign_keys=[wholesaler_id], backref="dukandar_relations")
    retailer = relationship("User", foreign_keys=[retailer_id], backref="wholesaler_relations")

# ─── Admin System ─────────────────────────────────────────────────────────────────

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="admin")  # superadmin, admin, support
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ─── Support Tickets ──────────────────────────────────────────────────────────────

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_id = Column(String(12), nullable=True)  # short 12-char ticket ID
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    shop_name = Column(String, nullable=True)
    type = Column(String, nullable=False)        # Issue, Complaint, Refund, Inquiry, Suggestion
    priority = Column(String, default="normal")   # low, normal, high, urgent
    subject = Column(String, nullable=True)
    message = Column(String, nullable=False)
    status = Column(String, default="open")       # open, in_progress, resolved, closed
    admin_notes = Column(String, nullable=True)
    # Refund-specific fields
    refund_amount = Column(String, nullable=True)
    refund_reason = Column(String, nullable=True)
    txn_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref="support_tickets")

# ─── Admin Broadcast Notifications ───────────────────────────────────────────────

class AdminNotification(Base):
    __tablename__ = "admin_notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    notification_type = Column(String, default="broadcast")  # broadcast, update, alert, promotional
    target_audience = Column(String, default="all")           # all, specific_plan, specific_user
    target_plan = Column(String, nullable=True)               # starter, basic, professional, business
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    admin = relationship("AdminUser", backref="notifications_sent")

class UserNotification(Base):
    __tablename__ = "user_notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    admin_notification_id = Column(UUID(as_uuid=True), ForeignKey("admin_notifications.id"), nullable=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    notification_type = Column(String, default="info")       # info, warning, expiry, promotion, system
    is_read = Column(Boolean, default=False)
    link = Column(String, nullable=True)                      # Optional deep link
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="notifications")
    admin_notification = relationship("AdminNotification", backref="user_notifications")
