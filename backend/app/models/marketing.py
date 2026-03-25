from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Numeric, Boolean, Text, ForeignKey, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin
import enum


class CouponType(str, enum.Enum):
    percent      = "percent"       # percentage discount
    fixed        = "fixed"         # fixed amount
    free_shipping= "free_shipping"


class NewsletterStatus(str, enum.Enum):
    active       = "active"
    unsubscribed = "unsubscribed"


class NewsletterSource(str, enum.Enum):
    homepage = "homepage"
    footer   = "footer"
    checkout = "checkout"


class ChannelEventType(str, enum.Enum):
    visit       = "visit"
    add_to_cart = "add_to_cart"
    order       = "order"


class Coupon(Base, TimestampMixin):
    __tablename__ = "coupons"

    id:               Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    code:             Mapped[str]            = mapped_column(String(50), unique=True, nullable=False, index=True)
    type:             Mapped[str]            = mapped_column(String(20), nullable=False)   # percent|fixed|free_shipping
    value:            Mapped[float]          = mapped_column(Numeric(10, 2), default=0, nullable=False)
    min_order_amount: Mapped[Optional[float]]= mapped_column(Numeric(10, 2), nullable=True)
    max_uses:         Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)       # null = unlimited
    used_count:       Mapped[int]            = mapped_column(Integer, default=0, nullable=False)
    starts_at:        Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ends_at:          Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active:        Mapped[bool]           = mapped_column(Boolean, default=True, nullable=False)
    description:      Mapped[Optional[str]]  = mapped_column(String(255), nullable=True)

    banners: Mapped[list["Banner"]] = relationship(back_populates="coupon")


class Banner(Base, TimestampMixin):
    """Top announcement bar — links to a coupon optionally."""
    __tablename__ = "banners"

    id:        Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    title:     Mapped[str]           = mapped_column(String(255), nullable=False)
    subtitle:  Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    coupon_id: Mapped[Optional[int]] = mapped_column(ForeignKey("coupons.id", ondelete="SET NULL"), nullable=True)
    link_url:  Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ends_at:   Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)
    sort_order:Mapped[int]           = mapped_column(Integer, default=0, nullable=False)

    coupon: Mapped[Optional["Coupon"]] = relationship(back_populates="banners")


class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    email:         Mapped[str]           = mapped_column(String(191), unique=True, nullable=False, index=True)
    source:        Mapped[str]           = mapped_column(String(20), default="footer", nullable=False)  # homepage|footer|checkout
    status:        Mapped[str]           = mapped_column(String(20), default="active", nullable=False)
    language_code: Mapped[str]           = mapped_column(String(10), default="en", nullable=False)
    unsub_token:   Mapped[Optional[str]] = mapped_column(String(191), unique=True, nullable=True)  # GDPR one-click
    subscribed_at: Mapped[datetime]      = mapped_column(DateTime, server_default=func.now(), nullable=False)
    unsubscribed_at:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class MarketingChannel(Base, TimestampMixin):
    __tablename__ = "marketing_channels"

    id:        Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:      Mapped[str]           = mapped_column(String(100), nullable=False)
    ref_code:  Mapped[str]           = mapped_column(String(50), unique=True, nullable=False, index=True)
    platform:  Mapped[Optional[str]] = mapped_column(String(50), nullable=True)   # instagram|tiktok|google|etc
    is_active: Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)

    events: Mapped[list["ChannelEvent"]] = relationship(back_populates="channel", cascade="all, delete-orphan")


class ChannelEvent(Base):
    __tablename__ = "channel_events"

    id:         Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int]           = mapped_column(ForeignKey("marketing_channels.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id:   Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    event_type: Mapped[str]           = mapped_column(String(20), nullable=False)   # visit|add_to_cart|order
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime]      = mapped_column(DateTime, server_default=func.now(), nullable=False)

    channel: Mapped["MarketingChannel"] = relationship(back_populates="events")


# ── Forward refs ──────────────────────────────────────────────────────────────
from app.models.order import Order   # noqa: E402
