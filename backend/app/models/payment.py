from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Numeric, Boolean, Text, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id:                  Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id:            Mapped[int]            = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    provider:            Mapped[str]            = mapped_column(String(20), nullable=False)  # stripe|paypal|airwallex
    provider_payment_id: Mapped[Optional[str]]  = mapped_column(String(191), nullable=True, index=True)
    amount:              Mapped[float]          = mapped_column(Numeric(10, 2), nullable=False)
    currency:            Mapped[str]            = mapped_column(String(10), default="USD", nullable=False)
    status:              Mapped[str]            = mapped_column(String(30), nullable=False)  # pending|paid|failed|refunded
    raw_response:        Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    order: Mapped["Order"] = relationship(back_populates="payments")
    refunds: Mapped[list["Refund"]] = relationship(back_populates="payment", cascade="all, delete-orphan")


class Refund(Base, TimestampMixin):
    __tablename__ = "refunds"

    id:                 Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    payment_id:         Mapped[int]            = mapped_column(ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_refund_id: Mapped[Optional[str]]  = mapped_column(String(255), nullable=True)
    amount:             Mapped[float]          = mapped_column(Numeric(10, 2), nullable=False)
    reason:             Mapped[Optional[str]]  = mapped_column(String(255), nullable=True)
    status:             Mapped[str]            = mapped_column(String(30), nullable=False, default="pending")
    processed_by:       Mapped[Optional[int]]  = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)

    payment: Mapped["Payment"] = relationship(back_populates="refunds")


class PaymentWebhook(Base):
    __tablename__ = "payment_webhooks"

    id:           Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider:     Mapped[str]            = mapped_column(String(20), nullable=False, index=True)
    event_type:   Mapped[str]            = mapped_column(String(100), nullable=False, index=True)
    event_id:     Mapped[Optional[str]]  = mapped_column(String(191), nullable=True, unique=True, index=True)  # dedup
    order_id:     Mapped[Optional[int]]  = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    status:       Mapped[str]            = mapped_column(String(20), default="received", nullable=False)
    raw_payload:  Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_msg:    Mapped[Optional[str]]  = mapped_column(Text, nullable=True)
    created_at:   Mapped[datetime]       = mapped_column(DateTime, server_default=func.now(), nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class PaymentFailedEmailLog(Base):
    """Dedup table — max 1 payment-failed email per order."""
    __tablename__ = "payment_failed_email_logs"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id:   Mapped[int]      = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    sent_at:    Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


# ── Forward refs ──────────────────────────────────────────────────────────────
from app.models.order import Order   # noqa: E402
from app.models.admin import Admin   # noqa: E402
