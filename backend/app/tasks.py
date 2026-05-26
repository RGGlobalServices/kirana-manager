
from sqlalchemy.orm import Session
from .database.database import SessionLocal
from .models import models
from .api.notifications import send_push_notification
from datetime import datetime, timedelta, date
from sqlalchemy import func
import os

def check_expiry_notifications(db: Session):
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
            models.UserNotification.created_at >= now - timedelta(hours=23)
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

def run_daily_notifications():
    db = SessionLocal()
    try:
        check_expiry_notifications(db)
        db.commit()
        # 1. Identify users who want notifications
        settings = db.query(models.NotificationSetting).all()
        
        for s in settings:
            user = db.query(models.User).filter(models.User.id == s.user_id).first()
            if not user: continue
            
            # Find the shop for this user
            shop = db.query(models.Shop).filter(models.Shop.owner_id == user.id).first()
            if not shop: continue
            
            messages = []
            
            # --- Low Stock Alert ---
            if s.low_stock_alert_enabled:
                low_stock_items = db.query(models.Product).filter(
                    models.Product.shop_id == shop.id,
                    models.Product.current_stock <= models.Product.min_stock
                ).all()
                
                if low_stock_items:
                    count = len(low_stock_items)
                    item_names = ", ".join([p.name for p in low_stock_items[:2]])
                    if count > 2:
                        item_names += f" and {count - 2} others"
                    messages.append({
                        "title": "📉 Low Stock Alert",
                        "body": f"You have {count} items running low: {item_names}. Restock soon!",
                        "tag": "stock-alert"
                    })
            
            # --- Yesterday's Profit ---
            if s.daily_summary_enabled:
                yesterday = (datetime.now() - timedelta(days=1)).date()
                stats = db.query(
                    func.sum(models.Sale.total_amount).label("sales"),
                    func.sum(models.Sale.total_profit).label("profit")
                ).filter(
                    models.Sale.shop_id == shop.id,
                    func.date(models.Sale.created_at) == yesterday
                ).first()
                
                if stats and (stats.sales or 0) > 0:
                    messages.append({
                        "title": "💰 Yesterday's Summary",
                        "body": f"Sales: ₹{stats.sales:,.0f} | Profit: ₹{stats.profit:,.0f}. Great job!",
                        "tag": "daily-summary"
                    })
            
            # Send notifications to all active subscriptions of this user
            if messages:
                subscriptions = db.query(models.PushSubscription).filter(
                    models.PushSubscription.user_id == user.id
                ).all()
                
                for sub in subscriptions:
                    for msg in messages:
                        send_push_notification(sub, msg)
                        
    finally:
        db.close()

if __name__ == "__main__":
    # For manual testing
    run_daily_notifications()
