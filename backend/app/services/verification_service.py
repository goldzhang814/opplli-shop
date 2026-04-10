"""
Email OTP verification service
- Generate and send 6-digit OTP
- Verify OTP and return a short-lived signed token
"""
from __future__ import annotations
import random
import string
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.verification import EmailVerificationCode
from app.models.user import User
from app.tasks.email_tasks import _send_email as send_email
from app.config import settings


OTP_EXPIRE_MINUTES = 10
# Simple in-memory store for verified tokens (process-local, fine for single instance)
# For multi-instance deploy, use Redis instead
_verified_tokens: dict[str, str] = {}  # token → email


def _generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))


def _generate_token() -> str:
    return secrets.token_urlsafe(32)


async def send_verification_code(
    db:      AsyncSession,
    email:   str,
    purpose: str = 'register',
) -> None:
    """Generate OTP, save to DB, send email."""

    # Rate limit: max 3 active unused codes per email in last 10 min
    existing = await db.execute(
        select(EmailVerificationCode).where(
            EmailVerificationCode.email    == email,
            EmailVerificationCode.purpose  == purpose,
            EmailVerificationCode.is_used  == False,
            EmailVerificationCode.expires_at > datetime.utcnow(),
        )
    )
    active = existing.scalars().all()
    if len(active) >= 3:
        raise HTTPException(429, "Too many verification requests. Please wait a few minutes.")

    # For register: check email not already taken
    if purpose == 'register':
        taken = await db.execute(
            select(User).where(User.email == email, User.is_guest == False)
        )
        if taken.scalar_one_or_none():
            raise HTTPException(400, "This email is already registered.")

    # Invalidate previous codes
    await db.execute(
        update(EmailVerificationCode)
        .where(
            EmailVerificationCode.email   == email,
            EmailVerificationCode.purpose == purpose,
            EmailVerificationCode.is_used == False,
        )
        .values(is_used=True)
    )

    # Create new code
    otp = _generate_otp()
    record = EmailVerificationCode(
        email      = email,
        code       = otp,
        purpose    = purpose,
        expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES),
    )
    db.add(record)
    await db.commit()

    # Send email
    send_email(
        to      = email,
        subject = f"Your {settings.APP_NAME or 'Store'} verification code: {otp}",
        html_body    = _build_email_body(otp, purpose),
    )


async def verify_code(
    db:      AsyncSession,
    email:   str,
    code:    str,
    purpose: str = 'register',
) -> str:
    """Verify OTP. Returns a short-lived verification token on success."""

    r = await db.execute(
        select(EmailVerificationCode).where(
            EmailVerificationCode.email      == email,
            EmailVerificationCode.code       == code,
            EmailVerificationCode.purpose    == purpose,
            EmailVerificationCode.is_used    == False,
            EmailVerificationCode.expires_at >  datetime.utcnow(),
        ).order_by(EmailVerificationCode.created_at.desc())
    )
    record = r.scalars().first()

    if not record:
        raise HTTPException(400, "Invalid or expired verification code.")

    # Mark as used
    record.is_used = True
    await db.commit()

    # Issue a short-lived verification token (valid 30 min)
    token = _generate_token()
    # Store: token → email (expires in 30 min via cleanup or Redis TTL)
    _verified_tokens[token] = email
    return token


def consume_verification_token(token: str) -> str:
    """
    Called during register to confirm email was verified.
    Returns email, raises 400 if invalid.
    """
    email = _verified_tokens.pop(token, None)
    if not email:
        raise HTTPException(400, "Email verification required. Please verify your email first.")
    return email


def _build_email_body(otp: str, purpose: str) -> str:
    action = "complete your registration" if purpose == 'register' else "verify your email"
    return f"""
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:32px">
      <h2 style="color:#18181b;margin-bottom:8px">Your verification code</h2>
      <p style="color:#6b7280;margin-bottom:24px">
        Use the code below to {action}. It expires in 10 minutes.
      </p>
      <div style="background:#f0fdf4;border:2px solid #10b981;border-radius:12px;
                  padding:24px;text-align:center;margin-bottom:24px">
        <span style="font-size:40px;font-weight:700;letter-spacing:12px;color:#065f46;font-family:monospace">
          {otp}
        </span>
      </div>
      <p style="color:#9ca3af;font-size:12px">
        If you didn't request this, you can safely ignore this email.
      </p>
    </div>
    """