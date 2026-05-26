from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Optional
import os
import secrets
import logging
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models import models
from .deps import get_current_user
from ..utils.email import send_ticket_confirmation_user, send_ticket_notification_team, send_refund_request_team


def short_ticket_id() -> str:
    """Generate a 12-character alphanumeric ticket ID (e.g. 4XK9M2P7QR8F)."""
    return secrets.token_hex(6).upper()

router = APIRouter()
logger = logging.getLogger(__name__)

class ContactRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    shop_name: Optional[str] = None
    type: str
    subject: Optional[str] = None
    message: str
    refund_amount: Optional[str] = None
    refund_reason: Optional[str] = None
    txn_id: Optional[str] = None

class TicketCreate(BaseModel):
    type: str
    subject: Optional[str] = None
    message: str
    priority: str = "normal"
    refund_amount: Optional[str] = None
    refund_reason: Optional[str] = None
    txn_id: Optional[str] = None

@router.post("/contact")
async def contact_support(req: ContactRequest, background_tasks: BackgroundTasks):
    try:
        ticket_id = short_ticket_id()

        # Send notification to support team
        if req.type == "Refund":
            background_tasks.add_task(
                send_refund_request_team,
                req.name, req.email, req.phone or "", req.shop_name or "",
                ticket_id, req.refund_amount or "", req.refund_reason or "", req.txn_id or "",
                req.message
            )
        else:
            background_tasks.add_task(
                send_ticket_notification_team,
                req.name, req.email, req.phone or "", req.shop_name or "",
                ticket_id, req.type, req.subject or "", req.message, "normal",
                f"Amount: {req.refund_amount or 'N/A'}, Reason: {req.refund_reason or 'N/A'}" if req.type == "Refund" else ""
            )

        # Send confirmation to user
        background_tasks.add_task(
            send_ticket_confirmation_user,
            req.name, req.email, ticket_id, req.type, req.subject or "", req.message
        )

        return {
            "status": "success",
            "message": "Support request received! Aapke email par confirmation bhej di gayi hai. Hum jald contact karenge.",
            "ticket_id": ticket_id
        }
    except Exception as e:
        logger.error(f"Error processing support request: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not process support request.")

@router.post("/tickets")
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    shop = db.query(models.Shop).filter(models.Shop.owner_id == user.id).first()

    display_id = short_ticket_id()
    db_ticket = models.SupportTicket(
        display_id=display_id,
        user_id=user.id,
        name=user.full_name,
        email=user.email,
        phone=None,
        shop_name=shop.name if shop else None,
        type=ticket.type,
        priority=ticket.priority,
        subject=ticket.subject,
        message=ticket.message,
        refund_amount=ticket.refund_amount,
        refund_reason=ticket.refund_reason,
        txn_id=ticket.txn_id,
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    ticket_id = display_id

    # Send notification to support team
    try:
        if ticket.type == "Refund":
            send_refund_request_team(
                user.full_name, user.email, "", shop.name if shop else "",
                ticket_id, ticket.refund_amount or "0", ticket.refund_reason or "", ticket.txn_id or "",
                ticket.message
            )
        else:
            send_ticket_notification_team(
                user.full_name, user.email, "", shop.name if shop else "",
                ticket_id, ticket.type, ticket.subject or "", ticket.message, ticket.priority
            )
        # Send confirmation to user
        send_ticket_confirmation_user(
            user.full_name, user.email, ticket_id, ticket.type, ticket.subject or "", ticket.message
        )
    except Exception as e:
        logger.error(f"Email sending failed (ticket saved): {e}")

    return {
        "status": "success",
        "message": "Ticket created successfully! Aapke email par confirmation bhej di gayi hai.",
        "ticket_id": ticket_id,
        "ticket": {
            "id": ticket_id,
            "display_id": ticket_id,
            "type": db_ticket.type,
            "status": db_ticket.status,
            "created_at": db_ticket.created_at.isoformat() if db_ticket.created_at else None
        }
    }

@router.get("/tickets")
def get_my_tickets(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    tickets = db.query(models.SupportTicket).filter(
        models.SupportTicket.user_id == user.id
    ).order_by(models.SupportTicket.created_at.desc()).all()

    return {
        "tickets": [
            {
                "id": str(t.id),
                "display_id": t.display_id or str(t.id)[:12].upper(),
                "type": t.type,
                "subject": t.subject,
                "message": t.message,
                "status": t.status,
                "priority": t.priority,
                "admin_notes": t.admin_notes,
                "refund_amount": t.refund_amount,
                "refund_reason": t.refund_reason,
                "txn_id": t.txn_id,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in tickets
        ]
    }

@router.get("/admin/tickets")
def list_all_tickets(
    db: Session = Depends(get_db)
):
    tickets = db.query(models.SupportTicket).order_by(
        models.SupportTicket.status,
        models.SupportTicket.created_at.desc()
    ).all()

    return {
        "tickets": [
            {
                "id": str(t.id),
                "display_id": t.display_id or str(t.id)[:12].upper(),
                "user_id": str(t.user_id) if t.user_id else None,
                "name": t.name,
                "email": t.email,
                "shop_name": t.shop_name,
                "type": t.type,
                "subject": t.subject,
                "message": t.message,
                "status": t.status,
                "priority": t.priority,
                "admin_notes": t.admin_notes,
                "refund_amount": t.refund_amount,
                "refund_reason": t.refund_reason,
                "txn_id": t.txn_id,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in tickets
        ],
        "total": len(tickets)
    }

class TicketUpdate(BaseModel):
    status: str
    admin_notes: Optional[str] = None

@router.patch("/admin/tickets/{ticket_id}")
def update_ticket(
    ticket_id: str,
    update: TicketUpdate,
    db: Session = Depends(get_db)
):
    ticket = db.query(models.SupportTicket).filter(models.SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = update.status
    if update.admin_notes:
        ticket.admin_notes = update.admin_notes
    if update.status == "resolved":
        from datetime import datetime
        ticket.resolved_at = datetime.now()

    db.commit()
    return {"status": "success", "message": "Ticket updated"}
