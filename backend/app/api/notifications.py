
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..database.database import get_db
from ..models import models
from .deps import get_current_user
import json
import os
import logging

logger = logging.getLogger(__name__)

# Make pywebpush optional — if missing, push notifications are disabled
try:
    from pywebpush import webpush, WebPushException
    PYWEBPUSH_AVAILABLE = True
except ImportError:
    PYWEBPUSH_AVAILABLE = False
    logger.warning("pywebpush not installed — push notifications disabled")

router = APIRouter()

class SubscriptionInfo(BaseModel):
    endpoint: str
    keys: dict

class NotificationSettingsUpdate(BaseModel):
    daily_summary_enabled: Optional[bool] = None
    low_stock_alert_enabled: Optional[bool] = None
    alert_time: Optional[bool] = None

@router.post("/subscribe")
def subscribe(
    subscription: SubscriptionInfo,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    try:
        existing = db.query(models.PushSubscription).filter(
            models.PushSubscription.endpoint == subscription.endpoint
        ).first()

        if existing:
            existing.user_id = user.id
            existing.p256dh = subscription.keys.get("p256dh", "")
            existing.auth = subscription.keys.get("auth", "")
        else:
            new_sub = models.PushSubscription(
                user_id=user.id,
                endpoint=subscription.endpoint,
                p256dh=subscription.keys.get("p256dh", ""),
                auth=subscription.keys.get("auth", "")
            )
            db.add(new_sub)

        db.commit()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Subscribe error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to subscribe: {str(e)}")

@router.get("/settings")
def get_settings(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    settings = db.query(models.NotificationSetting).filter(
        models.NotificationSetting.user_id == user.id
    ).first()

    if not settings:
        settings = models.NotificationSetting(user_id=user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings

@router.patch("/settings")
def update_settings(
    update: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    settings = db.query(models.NotificationSetting).filter(
        models.NotificationSetting.user_id == user.id
    ).first()

    if not settings:
        settings = models.NotificationSetting(user_id=user.id)
        db.add(settings)

    if update.daily_summary_enabled is not None:
        settings.daily_summary_enabled = update.daily_summary_enabled
    if update.low_stock_alert_enabled is not None:
        settings.low_stock_alert_enabled = update.low_stock_alert_enabled

    db.commit()
    return settings

@router.get("/in-app")
def get_in_app_notifications(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    notifications = db.query(models.UserNotification).filter(
        models.UserNotification.user_id == user.id
    ).order_by(models.UserNotification.created_at.desc()).limit(50).all()

    unread_count = db.query(models.UserNotification).filter(
        models.UserNotification.user_id == user.id,
        models.UserNotification.is_read == False
    ).count()

    return {
        "notifications": [
            {
                "id": str(n.id),
                "title": n.title,
                "message": n.message,
                "type": n.notification_type,
                "is_read": n.is_read,
                "link": n.link,
                "created_at": n.created_at.isoformat() if n.created_at else None
            }
            for n in notifications
        ],
        "unread_count": unread_count
    }

@router.post("/in-app/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    notification = db.query(models.UserNotification).filter(
        models.UserNotification.id == notification_id,
        models.UserNotification.user_id == user.id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()
    return {"status": "success"}

@router.post("/in-app/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    db.query(models.UserNotification).filter(
        models.UserNotification.user_id == user.id,
        models.UserNotification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"status": "success"}

def check_subscription_expiry():
    from ..database.database import SessionLocal
    db = SessionLocal()
    try:
        from datetime import datetime, timedelta
        now = datetime.now()
        warning_date = now + timedelta(days=3)

        expiring_shops = db.query(models.Shop).filter(
            models.Shop.subscription_expiry != None,
            models.Shop.subscription_expiry <= warning_date,
            models.Shop.subscription_expiry > now,
            models.Shop.subscription_status.in_(["active", "trialing"])
        ).all()

        for shop in expiring_shops:
            days_left = (shop.subscription_expiry - now).days
            existing = db.query(models.UserNotification).filter(
                models.UserNotification.user_id == shop.owner_id,
                models.UserNotification.notification_type == "expiry",
                models.UserNotification.created_at >= now - timedelta(days=1)
            ).first()
            if not existing:
                notif = models.UserNotification(
                    user_id=shop.owner_id,
                    title="Subscription Expiring Soon",
                    message=f"Your {shop.subscription_plan} plan will expire in {days_left} days. Renew now to continue using Vyapar Sarthi.",
                    notification_type="expiry",
                    link="/settings"
                )
                db.add(notif)

        db.commit()
    finally:
        db.close()

def send_push_notification(subscription: models.PushSubscription, message: dict):
    if not PYWEBPUSH_AVAILABLE:
        logger.warning("pywebpush not installed — skipping push notification")
        return False
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth
                }
            },
            data=json.dumps(message),
            vapid_private_key=os.getenv("VAPID_PRIVATE_KEY"),
            vapid_claims={"sub": f"mailto:{os.getenv('VAPID_CLAIM_EMAIL')}"}
        )
        return True
    except WebPushException as ex:
        logger.error(f"Web Push Error: {ex}")
        return False
