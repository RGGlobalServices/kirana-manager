import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "gbroindustries@gmail.com")

def send_email(to_emails: list[str], subject: str, html_body: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP not configured — skipping email send")
        print(f"[EMAIL] To: {to_emails}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Body (first 500 chars): {html_body[:500]}")
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(to_emails)
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Email sent to {to_emails}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        print(f"[EMAIL ERROR] {e}")

def send_ticket_confirmation_user(name: str, user_email: str, ticket_id: str, ticket_type: str, subject: str, message: str):
    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background: #f9fafb; border-radius: 16px;">
        <div style="text-align: center; margin-bottom: 24px;">
            <span style="font-size: 40px;">🛒</span>
            <h1 style="color: #1e293b; margin: 8px 0 0; font-size: 24px;">Vyapar Sarthi</h1>
            <p style="color: #64748b; font-size: 14px;">Support Ticket Confirmation</p>
        </div>
        <div style="background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <p style="color: #1e293b; font-size: 16px;">Namaste <strong>{name}</strong>,</p>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                Aapki ticket humein mil gayi hai. Hamari team jald hi aapki problem solve karegi.
            </p>
            <div style="background: #f1f5f9; border-radius: 10px; padding: 16px; margin: 16px 0;">
                <p style="margin: 0 0 8px; font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 1px;">Ticket Details</p>
                <table style="width: 100%; font-size: 14px; color: #334155;">
                    <tr><td style="padding: 4px 0; color: #64748b;">Ticket ID</td><td style="padding: 4px 0; font-weight: 700;">{ticket_id}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Type</td><td style="padding: 4px 0;">{ticket_type}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Subject</td><td style="padding: 4px 0;">{subject or '—'}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Status</td><td style="padding: 4px 0;"><span style="background: #fef3c7; color: #92400e; padding: 2px 10px; border-radius: 100px; font-size: 12px;">Open</span></td></tr>
                </table>
            </div>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                <strong>Aapka Message:</strong><br>
                {message}
            </p>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                Hum aapse 24 ghante mein contact karenge. Bechain na ho — hum hain na! 🎯
            </p>
        </div>
        <div style="text-align: center; margin-top: 24px; color: #94a3b8; font-size: 12px;">
            <p>Vyapar Sarthi — A product of GBRO Industries</p>
            <p>Email: gbroindustries@gmail.com | WhatsApp: Available 10 AM - 7 PM</p>
        </div>
    </div>
    """
    send_email([user_email], f"Ticket #{ticket_id[:8]} — Confirmation", html)

def send_ticket_notification_team(name: str, email: str, phone: str, shop_name: str, ticket_id: str, ticket_type: str, subject: str, message: str, priority: str, refund_details: str = ""):
    refund_section = f"""
    <tr><td style="padding: 4px 0; color: #64748b;">Refund Details</td><td style="padding: 4px 0;">{refund_details}</td></tr>
    """ if refund_details else ""

    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background: #f9fafb; border-radius: 16px;">
        <div style="text-align: center; margin-bottom: 24px;">
            <span style="font-size: 40px;">🔔</span>
            <h1 style="color: #1e293b; margin: 8px 0 0; font-size: 24px;">New Support Ticket</h1>
            <p style="color: #64748b; font-size: 14px;">Action Required</p>
        </div>
        <div style="background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <p style="color: #1e293b; font-size: 16px;">A new support ticket has been raised.</p>
            <div style="background: #f1f5f9; border-radius: 10px; padding: 16px; margin: 16px 0;">
                <p style="margin: 0 0 8px; font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 1px;">Customer Details</p>
                <table style="width: 100%; font-size: 14px; color: #334155;">
                    <tr><td style="padding: 4px 0; color: #64748b;">Name</td><td style="padding: 4px 0; font-weight: 700;">{name}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Email</td><td style="padding: 4px 0;"><a href="mailto:{email}" style="color: #4f46e5;">{email}</a></td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Phone</td><td style="padding: 4px 0;">{phone or '—'}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Shop</td><td style="padding: 4px 0;">{shop_name or '—'}</td></tr>
                    {refund_section}
                </table>
            </div>
            <div style="background: #f1f5f9; border-radius: 10px; padding: 16px; margin: 16px 0;">
                <p style="margin: 0 0 8px; font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 1px;">Ticket Details</p>
                <table style="width: 100%; font-size: 14px; color: #334155;">
                    <tr><td style="padding: 4px 0; color: #64748b;">Ticket ID</td><td style="padding: 4px 0; font-weight: 700;">{ticket_id}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Type</td><td style="padding: 4px 0;">{ticket_type}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Priority</td><td style="padding: 4px 0;">{priority}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Subject</td><td style="padding: 4px 0;">{subject or '—'}</td></tr>
                </table>
            </div>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                <strong>Message:</strong><br>
                {message}
            </p>
            <div style="margin-top: 20px; text-align: center;">
                <p style="color: #64748b; font-size: 13px;">Reply to this email to respond to the customer, or use the admin panel.</p>
            </div>
        </div>
    </div>
    """
    send_email([SUPPORT_EMAIL], f"[Ticket #{ticket_id[:8]}] {ticket_type}: {subject or name}", html)

def send_refund_request_team(name: str, email: str, phone: str, shop_name: str, ticket_id: str, refund_amount: str, refund_reason: str, txn_id: str, message: str):
    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background: #f9fafb; border-radius: 16px;">
        <div style="text-align: center; margin-bottom: 24px;">
            <span style="font-size: 40px;">💰</span>
            <h1 style="color: #1e293b; margin: 8px 0 0; font-size: 24px;">Refund Request</h1>
            <p style="color: #64748b; font-size: 14px;">Payment Action Required</p>
        </div>
        <div style="background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <p style="color: #1e293b; font-size: 16px;">A refund request has been submitted.</p>
            <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; padding: 16px; margin: 16px 0;">
                <table style="width: 100%; font-size: 14px; color: #334155;">
                    <tr><td style="padding: 4px 0; color: #64748b;">Name</td><td style="padding: 4px 0; font-weight: 700;">{name}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Email</td><td style="padding: 4px 0;"><a href="mailto:{email}" style="color: #4f46e5;">{email}</a></td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Phone</td><td style="padding: 4px 0;">{phone or '—'}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Shop</td><td style="padding: 4px 0;">{shop_name or '—'}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Ticket ID</td><td style="padding: 4px 0; font-weight: 700;">{ticket_id}</td></tr>
                    <tr><td style="padding: 4px 0; color: #ef4444; font-weight: 700;">Refund Amount</td><td style="padding: 4px 0; color: #ef4444; font-weight: 700; font-size: 18px;">₹{refund_amount}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Transaction ID</td><td style="padding: 4px 0;">{txn_id or '—'}</td></tr>
                    <tr><td style="padding: 4px 0; color: #64748b;">Refund Reason</td><td style="padding: 4px 0;">{refund_reason}</td></tr>
                </table>
            </div>
            <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                <strong>Additional Message:</strong><br>
                {message}
            </p>
            <p style="color: #ef4444; font-size: 13px; margin-top: 16px;">
                ⚠️ Please process this refund manually from the PayU dashboard and update the ticket status.
            </p>
        </div>
    </div>
    """
    send_email([SUPPORT_EMAIL], f"[REFUND] #{ticket_id[:8]} — ₹{refund_amount} — {name}", html)

def send_password_reset_user(user_email: str, reset_link: str):
    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background: #f9fafb; border-radius: 16px;">
        <div style="text-align: center; margin-bottom: 24px;">
            <span style="font-size: 40px;">🔐</span>
            <h1 style="color: #1e293b; margin: 8px 0 0; font-size: 24px;">Reset Your Password</h1>
            <p style="color: #64748b; font-size: 14px;">Vyapar Sarthi Account Security</p>
        </div>
        <div style="background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <p style="color: #334155; font-size: 14px; line-height: 1.6;">
                We received a request to reset your Vyapar Sarthi password.
            </p>
            <div style="text-align:center; margin: 18px 0;">
                <a href="{reset_link}" style="display:inline-block;background:#4f46e5;color:#fff;padding:12px 18px;border-radius:12px;text-decoration:none;font-weight:700;">
                    Reset Password
                </a>
            </div>
            <p style="color: #64748b; font-size: 13px; line-height: 1.6;">
                This link expires in 30 minutes. If you did not request this, you can ignore this email.
            </p>
            <p style="color:#64748b;font-size:12px;word-break:break-all;margin-top:12px;">
                Or copy this link: {reset_link}
            </p>
        </div>
        <div style="text-align: center; margin-top: 24px; color: #94a3b8; font-size: 12px;">
            <p>Vyapar Sarthi — A product of GBRO Industries</p>
        </div>
    </div>
    """
    send_email([user_email], "Reset your Vyapar Sarthi password", html)
