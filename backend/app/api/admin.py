from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
import os
from jose import JWTError, jwt
from ..database.database import get_db
from ..models import models
from ..api.auth_utils import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM

router = APIRouter()

def get_admin_user(
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id: str = payload.get("sub")
        if admin_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    admin = db.query(models.AdminUser).filter(models.AdminUser.id == admin_id).first()
    if not admin or not admin.is_active:
        raise HTTPException(status_code=401, detail="Admin not found or inactive")
    return admin

class AdminLoginRequest(BaseModel):
    email: str
    password: str

class AdminRegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    secret_key: str

@router.post("/login")
def admin_login(req: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = db.query(models.AdminUser).filter(models.AdminUser.email == req.email).first()
    if not admin or not verify_password(req.password, admin.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Admin account is deactivated")

    token = create_access_token(data={"sub": str(admin.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "admin": {
            "id": str(admin.id),
            "email": admin.email,
            "name": admin.full_name,
            "role": admin.role
        }
    }

@router.post("/register")
def admin_register(req: AdminRegisterRequest, db: Session = Depends(get_db)):
    if req.secret_key != os.getenv("ADMIN_SECRET_KEY", "vyapar-sarthi-admin-secret-2025"):
        raise HTTPException(status_code=403, detail="Invalid secret key")

    existing = db.query(models.AdminUser).filter(models.AdminUser.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    admin = models.AdminUser(
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    token = create_access_token(data={"sub": str(admin.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "admin": {
            "id": str(admin.id),
            "email": admin.email,
            "name": admin.full_name,
            "role": admin.role
        }
    }

@router.get("/me")
def admin_me(admin: models.AdminUser = Depends(get_admin_user)):
    return {
        "id": str(admin.id),
        "email": admin.email,
        "name": admin.full_name,
        "role": admin.role
    }

@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    admin: models.AdminUser = Depends(get_admin_user)
):
    users = db.query(models.User).all()
    result = []
    for u in users:
        shop = db.query(models.Shop).filter(models.Shop.owner_id == u.id).first()
        result.append({
            "id": str(u.id),
            "email": u.email,
            "name": u.full_name,
            "is_active": u.is_active,
            "shop_name": shop.name if shop else "N/A",
            "plan": shop.subscription_plan if shop else "N/A",
            "subscription_status": shop.subscription_status if shop else "N/A",
            "subscription_expiry": shop.subscription_expiry.isoformat() if shop and shop.subscription_expiry else None,
            "created_at": shop.created_at.isoformat() if shop and shop.created_at else None
        })
    return {"users": result, "total": len(result)}

@router.get("/users/{user_id}")
def get_user_detail(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: models.AdminUser = Depends(get_admin_user)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shop = db.query(models.Shop).filter(models.Shop.owner_id == user.id).first()
    referrals_given = db.query(models.Referral).filter(
        models.Referral.referrer_id == user.id
    ).count()
    referrals_received = db.query(models.Referral).filter(
        models.Referral.referred_id == user.id
    ).count()

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.full_name,
        "is_active": user.is_active,
        "shop": {
            "id": str(shop.id),
            "name": shop.name,
            "business_type": shop.business_type,
            "plan": shop.subscription_plan,
            "subscription_status": shop.subscription_status,
            "subscription_expiry": shop.subscription_expiry.isoformat() if shop.subscription_expiry else None
        } if shop else None,
        "referrals_given": referrals_given,
        "referrals_received": referrals_received
    }

class BlockUserRequest(BaseModel):
    is_active: int

@router.patch("/users/{user_id}/status")
def toggle_user_status(
    user_id: UUID,
    req: BlockUserRequest,
    db: Session = Depends(get_db),
    admin: models.AdminUser = Depends(get_admin_user)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = req.is_active
    db.commit()
    return {"status": "success", "message": f"User {'activated' if req.is_active else 'blocked'} successfully"}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: models.AdminUser = Depends(get_admin_user)
):
    if admin.role not in ["superadmin"]:
        raise HTTPException(status_code=403, detail="Only superadmin can delete users")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shop = db.query(models.Shop).filter(models.Shop.owner_id == user.id).first()
    if shop:
        sid = shop.id
        # Delete sale_items first (FK references products via product_id)
        db.query(models.SaleItem).filter(
            models.SaleItem.sale_id.in_(
                db.query(models.Sale.id).filter(models.Sale.shop_id == sid)
            )
        ).delete(synchronize_session=False)
        # Delete stock_logs (FK references products)
        db.query(models.StockLog).filter(models.StockLog.shop_id == sid).delete()
        db.query(models.Product).filter(models.Product.shop_id == sid).delete()
        db.query(models.Customer).filter(models.Customer.shop_id == sid).delete()
        db.query(models.Sale).filter(models.Sale.shop_id == sid).delete()
        db.delete(shop)
    db.query(models.Referral).filter(
        (models.Referral.referrer_id == user.id) | (models.Referral.referred_id == user.id)
    ).delete()
    db.query(models.PushSubscription).filter(models.PushSubscription.user_id == user.id).delete()
    db.query(models.NotificationSetting).filter(models.NotificationSetting.user_id == user.id).delete()
    db.query(models.ReferralCode).filter(models.ReferralCode.user_id == user.id).delete()
    db.query(models.DukandarRelationship).filter(
        (models.DukandarRelationship.wholesaler_id == user.id) | (models.DukandarRelationship.retailer_id == user.id)
    ).delete()
    db.query(models.SupportTicket).filter(models.SupportTicket.user_id == user.id).delete()
    db.query(models.UserNotification).filter(models.UserNotification.user_id == user.id).delete()
    db.delete(user)
    db.commit()
    return {"status": "success", "message": "User and all associated data deleted"}

@router.patch("/users/{user_id}/plan")
def update_user_plan(
    user_id: UUID,
    req: dict,
    db: Session = Depends(get_db),
    admin: models.AdminUser = Depends(get_admin_user)
):
    plan = req.get("plan")
    status_val = req.get("status")
    expiry_days = req.get("expiry_days")

    shop = db.query(models.Shop).filter(models.Shop.owner_id == user_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    if plan:
        shop.subscription_plan = plan
    if status_val:
        shop.subscription_status = status_val
    if expiry_days:
        shop.subscription_expiry = datetime.now() + timedelta(days=expiry_days)

    db.commit()
    return {"status": "success", "message": "Plan updated"}

@router.get("/analytics")
def get_analytics(
    period: str = "daily",
    db: Session = Depends(get_db),
    admin: models.AdminUser = Depends(get_admin_user)
):
    total_users = db.query(models.User).count()
    total_active_users = db.query(models.User).filter(models.User.is_active == 1).count()
    total_shops = db.query(models.Shop).count()

    plan_counts = db.query(
        models.Shop.subscription_plan,
        func.count(models.Shop.id)
    ).group_by(models.Shop.subscription_plan).all()

    status_counts = db.query(
        models.Shop.subscription_status,
        func.count(models.Shop.id)
    ).group_by(models.Shop.subscription_status).all()

    now = datetime.now()
    if period == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "yearly":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    sales_query = db.query(func.sum(models.Sale.total_amount), func.sum(models.Sale.total_profit))
    sales_query = sales_query.filter(models.Sale.created_at >= start)
    total_sales, total_profit = sales_query.first() or (0, 0)
    total_sales = total_sales or 0
    total_profit = total_profit or 0

    total_referrals = db.query(models.Referral).count()
    successful_referrals = db.query(models.Referral).filter(
        models.Referral.status == "completed"
    ).count()

    return {
        "users": {
            "total": total_users,
            "active": total_active_users,
            "blocked": total_users - total_active_users
        },
        "subscriptions": {
            "total_shops": total_shops,
            "by_plan": {p: c for p, c in plan_counts},
            "by_status": {s: c for s, c in status_counts}
        },
        "revenue": {
            "total_sales": total_sales,
            "total_profit": total_profit
        },
        "referrals": {
            "total": total_referrals,
            "successful": successful_referrals
        },
        "period": period
    }

@router.get("/referrals")
def get_all_referrals(
    db: Session = Depends(get_db),
    admin: models.AdminUser = Depends(get_admin_user)
):
    referrals = db.query(models.Referral).order_by(models.Referral.created_at.desc()).all()
    result = []
    for ref in referrals:
        referrer = db.query(models.User).filter(models.User.id == ref.referrer_id).first()
        referred = db.query(models.User).filter(models.User.id == ref.referred_id).first() if ref.referred_id else None
        result.append({
            "id": str(ref.id),
            "referrer": referrer.full_name if referrer else "Unknown",
            "referrer_email": referrer.email if referrer else "N/A",
            "referred": referred.full_name if referred else "Pending",
            "referred_email": referred.email if referred else ref.referred_email,
            "code": ref.referral_code,
            "status": ref.status,
            "discount_applied": ref.discount_applied,
            "referrer_rewarded": ref.referrer_rewarded,
            "created_at": ref.created_at.isoformat() if ref.created_at else None
        })
    return {"referrals": result}

@router.post("/broadcast-notification")
def send_broadcast(
    notification: dict,
    db: Session = Depends(get_db),
    admin: models.AdminUser = Depends(get_admin_user)
):
    title = notification.get("title")
    message = notification.get("message")
    ntype = notification.get("type", "broadcast")
    target = notification.get("target", "all")
    target_plan = notification.get("target_plan")

    if not title or not message:
        raise HTTPException(status_code=400, detail="Title and message are required")

    admin_notif = models.AdminNotification(
        admin_id=admin.id,
        title=title,
        message=message,
        notification_type=ntype,
        target_audience=target,
        target_plan=target_plan
    )
    db.add(admin_notif)
    db.flush()

    query = db.query(models.User)
    if target == "specific_plan" and target_plan:
        shop_ids = db.query(models.Shop.id).filter(
            models.Shop.subscription_plan == target_plan
        ).subquery()
        query = query.filter(models.User.id.in_(
            db.query(models.Shop.owner_id).filter(models.Shop.subscription_plan == target_plan)
        ))

    users = query.all()
    for user in users:
        user_notif = models.UserNotification(
            user_id=user.id,
            admin_notification_id=admin_notif.id,
            title=title,
            message=message,
            notification_type=ntype
        )
        db.add(user_notif)

    db.commit()
    return {
        "status": "success",
        "message": f"Notification sent to {len(users)} users",
        "recipient_count": len(users)
    }

class SubscriptionActionRequest(BaseModel):
    action: str  # barrier, activate

@router.post("/users/{user_id}/subscription-action")
def subscription_action(
    user_id: UUID,
    req: SubscriptionActionRequest,
    db: Session = Depends(get_db),
    admin: models.AdminUser = Depends(get_admin_user)
):
    shop = db.query(models.Shop).filter(models.Shop.owner_id == user_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    if req.action == "barrier":
        shop.subscription_status = "cancelled"
        shop.subscription_expiry = datetime.now()
        msg = "Service barred"
    elif req.action == "activate":
        shop.subscription_status = "active"
        msg = "Service activated"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    db.commit()
    return {"status": "success", "message": msg}
