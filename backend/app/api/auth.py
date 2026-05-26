from datetime import timedelta, datetime
import os
import re
import json
from urllib.request import urlopen
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models import models
from ..schemas import schemas
from .auth_utils import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwk as jose_jwk
from ..utils.email import send_password_reset_user

router = APIRouter()

GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
_google_jwks_cache = None
_google_jwks_fetched_at = None

@router.post("/register", response_model=schemas.Token)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create a shop for this user
    from datetime import datetime, timedelta
    
    plan   = user_in.paid_plan if user_in.paid_plan else "starter"
    status = "active"
    expiry = None
    if plan != "starter":
        status = "trialing"
        expiry = datetime.now() + timedelta(days=14)

    new_shop = models.Shop(
        owner_id=new_user.id,
        name=user_in.shop_name,
        business_type=user_in.business_type,
        setup_complete=True,
        subscription_plan=plan,
        subscription_status=status,
        subscription_expiry=expiry
    )
    db.add(new_shop)
    db.commit()
    db.refresh(new_shop)
    
    # Return token for auto-login
    access_token = create_access_token(data={"sub": str(new_user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.full_name,
            "storeName": new_shop.name,
            "mobile":  new_shop.mobile,
        }
    }


@router.post("/login", response_model=schemas.Token)
def login(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Using UserCreate to accept email/password/shop_name (shop_name ignored in login)
    # Support login by email OR 10-digit mobile number
    user = None
    shop = None
    is_phone = bool(re.match(r'^\d{10}$', user_in.email))

    if is_phone:
        # Look up shop by mobile, then get the owning user
        shop = db.query(models.Shop).filter(models.Shop.mobile == user_in.email).first()
        if shop:
            user = db.query(models.User).filter(models.User.id == shop.owner_id).first()
    else:
        # Default: look up user by email
        user = db.query(models.User).filter(models.User.email == user_in.email).first()
        if user:
            shop = db.query(models.Shop).filter(models.Shop.owner_id == user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email. Please sign up first.")
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password. Please try again.")

    if not shop:
        shop = db.query(models.Shop).filter(models.Shop.owner_id == user.id).first()

    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.full_name,
            "storeName": shop.name if shop else "Vyapar Sarthi",
            "mobile":  shop.mobile if shop else None,
        }
    }


@router.post("/forgot-password")
def forgot_password(req: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()

    # Return a generic success message so account existence is not exposed.
    response = {
        "message": "If this email is registered, a password reset link has been sent."
    }
    if not user:
        return response

    token = create_access_token(
        data={"sub": str(user.id), "purpose": "password_reset"},
        expires_delta=timedelta(minutes=30),
    )
    landing_url = os.getenv("LANDING_URL", "http://localhost:5173").rstrip("/")
    reset_link = f"{landing_url}/reset-password.html?token={token}"

    # Send reset link via email when SMTP is configured.
    send_password_reset_user(user.email, reset_link)

    # For local development, optionally return the link in the API response.
    # Set PASSWORD_RESET_DEV_LINK=1 to expose it.
    if os.getenv("PASSWORD_RESET_DEV_LINK", "0") == "1":
        response["reset_link"] = reset_link
    return response


@router.post("/reset-password")
def reset_password(req: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    try:
        payload = jwt.decode(req.token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("purpose") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid reset token")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Reset link is invalid or expired")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Reset link is invalid or expired")

    user.hashed_password = get_password_hash(req.password)
    db.commit()
    return {"message": "Password updated successfully"}


def _fetch_google_jwks():
    global _google_jwks_cache, _google_jwks_fetched_at
    now = datetime.now()
    if _google_jwks_cache and _google_jwks_fetched_at and (now - _google_jwks_fetched_at).seconds < 3600:
        return _google_jwks_cache
    try:
        resp = urlopen(GOOGLE_JWKS_URL, timeout=10)
        _google_jwks_cache = json.loads(resp.read())
        _google_jwks_fetched_at = now
    except Exception:
        pass
    return _google_jwks_cache


def _verify_google_token(credential: str) -> dict:
    """Verify a Google ID token and return its payload."""
    jwks = _fetch_google_jwks()
    if not jwks:
        raise HTTPException(status_code=503, detail="Failed to fetch Google public keys")

    try:
        header = jwt.get_unverified_header(credential)
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    key = None
    for k in jwks.get("keys", []):
        if k.get("kid") == header.get("kid"):
            key = k
            break
    if not key:
        raise HTTPException(status_code=400, detail="Invalid Google token (key not found)")

    try:
        rsa_key = jose_jwk.construct(key)
        payload = jwt.decode(
            credential,
            rsa_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    return payload


@router.post("/google")
def google_login(req: schemas.GoogleAuthRequest, db: Session = Depends(get_db)):
    payload = _verify_google_token(req.credential)
    email = payload.get("email")
    name = payload.get("name", email.split("@")[0] if email else "Google User")

    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        temp_pass = get_password_hash(os.urandom(16).hex())
        user = models.User(
            email=email,
            hashed_password=temp_pass,
            full_name=name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        shop = models.Shop(
            owner_id=user.id,
            name=f"{name}'s Shop",
            business_type="kirana",
            setup_complete=True,
        )
        db.add(shop)
        db.commit()
    else:
        shop = db.query(models.Shop).filter(models.Shop.owner_id == user.id).first()

    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.full_name,
            "storeName": shop.name if shop else "Vyapar Sarthi",
            "mobile": shop.mobile if shop else None,
        }
    }
