import sys, uuid
sys.path.insert(0, ".")
from app.database.database import SessionLocal
from app.models import models

db = SessionLocal()

user = db.query(models.User).filter(models.User.email == "rahulgosavi529@gmail.com").first()
if not user:
    print("User not found")
    db.close()
    exit()

uid = user.id
print(f"Deleting: {user.email} (id: {uid})")

try:
    shop = db.query(models.Shop).filter(models.Shop.owner_id == uid).first()
    if shop:
        print(f"  Shop: {shop.name}")
        db.query(models.Product).filter(models.Product.shop_id == shop.id).delete()
        db.query(models.Customer).filter(models.Customer.shop_id == shop.id).delete()
        db.query(models.Sale).filter(models.Sale.shop_id == shop.id).delete()
        db.delete(shop)
    db.query(models.Referral).filter(
        (models.Referral.referrer_id == uid) | (models.Referral.referred_id == uid)
    ).delete()
    db.query(models.PushSubscription).filter(models.PushSubscription.user_id == uid).delete()
    db.query(models.NotificationSetting).filter(models.NotificationSetting.user_id == uid).delete()
    db.query(models.ReferralCode).filter(models.ReferralCode.user_id == uid).delete()
    db.query(models.DukandarRelationship).filter(
        (models.DukandarRelationship.wholesaler_id == uid) | (models.DukandarRelationship.retailer_id == uid)
    ).delete()
    db.query(models.SupportTicket).filter(models.SupportTicket.user_id == uid).delete()
    db.delete(user)
    db.commit()
    print("  SUCCESS")
except Exception as e:
    db.rollback()
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

db.close()
