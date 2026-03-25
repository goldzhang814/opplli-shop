"""
Celery Email Tasks
==================
All outgoing emails go through here.
Email provider: Resend (primary) → SendGrid (fallback) → SMTP
Template rendering uses EmailTemplate rows from DB + variable substitution.
"""
from __future__ import annotations
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from celery.utils.log import get_task_logger
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.config import settings
from app.models.content import EmailTemplate
from app.models.user import User

logger = get_task_logger(__name__)

# Sync engine for Celery tasks (Celery doesn't use asyncio)
_sync_engine = create_engine(
    settings.DATABASE_URL.replace("mysql+aiomysql", "mysql+pymysql"),
    pool_pre_ping=True,
)


def _get_template(db: Session, ttype: str, lang: str) -> Optional[EmailTemplate]:
    r = db.execute(
        select(EmailTemplate).where(
            EmailTemplate.type          == ttype,
            EmailTemplate.language_code == lang,
            EmailTemplate.is_active     == True,
        )
    ).scalar_one_or_none()
    if not r and lang != "en":
        # Fallback to English
        r = db.execute(
            select(EmailTemplate).where(
                EmailTemplate.type          == ttype,
                EmailTemplate.language_code == "en",
                EmailTemplate.is_active     == True,
            )
        ).scalar_one_or_none()
    return r


def _render(template: str, variables: dict) -> str:
    """Replace {{variable}} placeholders."""
    for k, v in variables.items():
        template = template.replace(f"{{{{{k}}}}}", str(v))
    return template


def _send_email(to: str, subject: str, html_body: str) -> None:
    provider = settings.EMAIL_PROVIDER

    if provider == "resend":
        import resend
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send({
            "from":    f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to":      [to],
            "subject": subject,
            "html":    html_body,
        })
        return

    if provider == "sendgrid":
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        msg = Mail(
            from_email    = settings.EMAIL_FROM,
            to_emails     = to,
            subject       = subject,
            html_content  = html_body,
        )
        SendGridAPIClient(settings.SENDGRID_API_KEY).send(msg)
        return

    # SMTP fallback
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.EMAIL_FROM
    msg["To"]      = to
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
        s.starttls()
        s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        s.sendmail(settings.EMAIL_FROM, [to], msg.as_string())


# ── Task: order confirmation ──────────────────────────────────────────────────
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation(self, *, order_id: int, email: str,
                             customer_name: str, language: str = "en"):
    try:
        with Session(_sync_engine) as db:
            tmpl = _get_template(db, "order_confirmation", language)
            if not tmpl:
                logger.warning("No order_confirmation template for lang=%s", language)
                return
            subject = _render(tmpl.subject, {"order_id": order_id, "customer_name": customer_name})
            body    = _render(tmpl.body,    {"order_id": order_id, "customer_name": customer_name})
        _send_email(email, subject, body)
        logger.info("order_confirmation sent → %s (order #%s)", email, order_id)
    except Exception as exc:
        logger.error("send_order_confirmation failed: %s", exc)
        raise self.retry(exc=exc)


# ── Task: order shipped ───────────────────────────────────────────────────────
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_shipped(self, *, order_id: int, email: str, customer_name: str,
                        carrier_name: str, tracking_no: str, tracking_url: str,
                        language: str = "en"):
    try:
        with Session(_sync_engine) as db:
            tmpl = _get_template(db, "order_shipped", language)
            if not tmpl:
                return
            vars_ = {"order_id": order_id, "customer_name": customer_name,
                     "carrier_name": carrier_name, "tracking_no": tracking_no,
                     "tracking_url": tracking_url}
            _send_email(email, _render(tmpl.subject, vars_), _render(tmpl.body, vars_))
        logger.info("order_shipped sent → %s", email)
    except Exception as exc:
        raise self.retry(exc=exc)


# ── Task: order cancelled ─────────────────────────────────────────────────────
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_cancelled(self, *, order_id: int, email: str,
                          customer_name: str, language: str = "en"):
    try:
        with Session(_sync_engine) as db:
            tmpl = _get_template(db, "order_cancelled", language)
            if not tmpl:
                return
            vars_ = {"order_id": order_id, "customer_name": customer_name}
            _send_email(email, _render(tmpl.subject, vars_), _render(tmpl.body, vars_))
    except Exception as exc:
        raise self.retry(exc=exc)


# ── Task: order refunded ──────────────────────────────────────────────────────
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_refunded(self, *, order_id: int, email: str, customer_name: str,
                         refund_amount: str, language: str = "en"):
    try:
        with Session(_sync_engine) as db:
            tmpl = _get_template(db, "order_refunded", language)
            if not tmpl:
                return
            vars_ = {"order_id": order_id, "customer_name": customer_name,
                     "refund_amount": refund_amount}
            _send_email(email, _render(tmpl.subject, vars_), _render(tmpl.body, vars_))
    except Exception as exc:
        raise self.retry(exc=exc)


# ── Task: payment failed (max 1 per order — DB dedup) ────────────────────────
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_payment_failed(self, *, order_id: int, email: str, customer_name: str,
                         fail_reason: str, retry_url: str, language: str = "en"):
    """
    Dedup via payment_failed_email_logs table.
    If a row already exists for order_id → skip silently.
    """
    from app.models.payment import PaymentFailedEmailLog
    try:
        with Session(_sync_engine) as db:
            existing = db.execute(
                select(PaymentFailedEmailLog).where(
                    PaymentFailedEmailLog.order_id == order_id
                )
            ).scalar_one_or_none()
            if existing:
                logger.info("payment_failed email already sent for order #%s, skipping", order_id)
                return

            tmpl = _get_template(db, "payment_failed", language)
            if not tmpl:
                return
            vars_ = {"order_id": order_id, "customer_name": customer_name,
                     "fail_reason": fail_reason, "retry_url": retry_url}
            _send_email(email, _render(tmpl.subject, vars_), _render(tmpl.body, vars_))

            # Record dedup
            db.add(PaymentFailedEmailLog(order_id=order_id))
            db.commit()
        logger.info("payment_failed sent → %s (order #%s)", email, order_id)
    except Exception as exc:
        raise self.retry(exc=exc)


# ── Task: password reset ──────────────────────────────────────────────────────
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, *, user_id: int, email: str,
                               token: str, language: str = "en"):
    try:
        reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        with Session(_sync_engine) as db:
            user = db.get(User, user_id)
            name = user.full_name or email if user else email
            tmpl = _get_template(db, "password_reset", language)
            if not tmpl:
                return
            vars_ = {"customer_name": name, "reset_url": reset_url}
            _send_email(email, _render(tmpl.subject, vars_), _render(tmpl.body, vars_))
    except Exception as exc:
        raise self.retry(exc=exc)


# ── Beat task: deactivate expired banners ─────────────────────────────────────
@celery_app.task
def deactivate_expired_banners():
    from datetime import datetime, timezone
    from sqlalchemy import update
    from app.models.marketing import Banner
    with Session(_sync_engine) as db:
        now = datetime.now(timezone.utc)
        db.execute(
            update(Banner)
            .where(Banner.ends_at <= now, Banner.is_active == True)
            .values(is_active=False)
        )
        db.commit()
    logger.info("Expired banners deactivated")
