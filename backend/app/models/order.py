from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy import (
    String, Integer, Numeric, Boolean, Text,
    ForeignKey, JSON, DateTime, func, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin
import enum


class OrderStatus(str, enum.Enum):
    pending_payment  = "pending_payment"
    pending_shipment = "pending_shipment"
    shipped          = "shipped"
    completed        = "completed"
    cancelled        = "cancelled"
    refund_requested = "refund_requested"
    refunded         = "refunded"


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id:               Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no:         Mapped[str]           = mapped_column(String(40), unique=True, nullable=False, index=True)
    user_id:          Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status:           Mapped[str]           = mapped_column(String(30), default="pending_payment", nullable=False, index=True)

    # Amounts (all USD)
    subtotal:         Mapped[float]         = mapped_column(Numeric(10, 2), nullable=False)
    shipping_fee:     Mapped[float]         = mapped_column(Numeric(10, 2), default=0, nullable=False)
    tax_amount:       Mapped[float]         = mapped_column(Numeric(10, 2), default=0, nullable=False)
    discount_amount:  Mapped[float]         = mapped_column(Numeric(10, 2), default=0, nullable=False)
    total_amount:     Mapped[float]         = mapped_column(Numeric(10, 2), nullable=False)

    # Payment
    payment_method:   Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # stripe|paypal|airwallex
    payment_status:   Mapped[str]           = mapped_column(String(30), default="unpaid", nullable=False)

    # Coupon
    coupon_code:      Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Addresses snapshot (JSON — immutable at order time)
    shipping_address: Mapped[Optional[dict]]= mapped_column(JSON, nullable=True)

    # Shipping zone / rule snapshot
    shipping_zone_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    shipping_rule_id:   Mapped[Optional[int]] = mapped_column(ForeignKey("shipping_rules.id", ondelete="SET NULL"), nullable=True)

    # Tax
    tax_rule_id:      Mapped[Optional[int]] = mapped_column(ForeignKey("tax_rules.id", ondelete="SET NULL"), nullable=True)
    tax_rate_snapshot:Mapped[Optional[float]]= mapped_column(Numeric(5, 4), nullable=True)

    # Channel tracking
    channel_ref:      Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    channel_id:       Mapped[Optional[int]] = mapped_column(ForeignKey("marketing_channels.id", ondelete="SET NULL"), nullable=True)

    # Guest
    guest_email:      Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Language
    language_code:    Mapped[str]           = mapped_column(String(10), default="en", nullable=False)

    # Note
    customer_note:    Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    admin_note:       Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user:        Mapped[Optional["User"]]       = relationship(back_populates="orders")
    items:       Mapped[list["OrderItem"]]       = relationship(back_populates="order", cascade="all, delete-orphan")
    payments:    Mapped[list["Payment"]]         = relationship(back_populates="order")
    shipment:    Mapped[Optional["Shipment"]]    = relationship(back_populates="order", uselist=False)
    status_logs: Mapped[list["OrderStatusLog"]]  = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id:              Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id:        Mapped[int]           = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    sku_id:          Mapped[Optional[int]] = mapped_column(ForeignKey("product_skus.id", ondelete="SET NULL"), nullable=True)
    product_name:    Mapped[str]           = mapped_column(String(255), nullable=False)   # snapshot
    sku_code:        Mapped[str]           = mapped_column(String(100), nullable=False)   # snapshot
    variant_attrs:   Mapped[Optional[dict]]= mapped_column(JSON, nullable=True)           # snapshot
    quantity:        Mapped[int]           = mapped_column(Integer, nullable=False)
    unit_price:      Mapped[float]         = mapped_column(Numeric(10, 2), nullable=False)# snapshot
    subtotal:        Mapped[float]         = mapped_column(Numeric(10, 2), nullable=False)
    product_image:   Mapped[Optional[str]] = mapped_column(String(500), nullable=True)   # snapshot

    order: Mapped["Order"]                       = relationship(back_populates="items")
    sku:   Mapped[Optional["ProductSku"]]        = relationship(back_populates="order_items")


class OrderStatusLog(Base):
    __tablename__ = "order_status_logs"

    id:         Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id:   Mapped[int]           = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status:Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    to_status:  Mapped[str]           = mapped_column(String(30), nullable=False)
    note:       Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    operator_id:Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime]      = mapped_column(DateTime, server_default=func.now(), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="status_logs")


# ── Forward refs ──────────────────────────────────────────────────────────────
from app.models.user import User                             # noqa: E402
from app.models.product import ProductSku                    # noqa: E402
from app.models.payment import Payment                       # noqa: E402
from app.models.shipping import Shipment, ShippingRule       # noqa: E402
from app.models.tax import TaxRule                           # noqa: E402
from app.models.marketing import MarketingChannel            # noqa: E402
from app.models.admin import Admin                           # noqa: E402
