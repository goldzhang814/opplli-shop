from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Numeric, Boolean, Text, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


# ── Layer 1: Deliverable Regions ─────────────────────────────────────────────
class ShippingRegion(Base, TimestampMixin):
    """
    Controls WHERE we ship. State-level granularity for US (HI/AK disabled).
    Other countries: state_code = NULL means whole country.
    """
    __tablename__ = "shipping_regions"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    country_code: Mapped[str]           = mapped_column(String(3), nullable=False, index=True)
    state_code:   Mapped[Optional[str]] = mapped_column(String(10), nullable=True)   # NULL = whole country
    enabled:      Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)


# ── Layer 2: Shipping Zones ───────────────────────────────────────────────────
class ShippingZone(Base, TimestampMixin):
    """Groups countries into pricing regions."""
    __tablename__ = "shipping_zones"

    id:   Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    country_mappings: Mapped[list["ShippingZoneRegion"]] = relationship(back_populates="zone", cascade="all, delete-orphan")
    rules:            Mapped[list["ShippingRule"]]        = relationship(back_populates="zone")


class ShippingZoneRegion(Base):
    """Maps countries → zones."""
    __tablename__ = "shipping_zone_regions"

    id:           Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id:      Mapped[int] = mapped_column(ForeignKey("shipping_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    country_code: Mapped[str] = mapped_column(String(3), nullable=False, index=True)

    zone: Mapped["ShippingZone"] = relationship(back_populates="country_mappings")


# ── Layer 3: Shipping Rules ───────────────────────────────────────────────────
class ShippingRule(Base, TimestampMixin):
    """Fee + free shipping threshold per zone."""
    __tablename__ = "shipping_rules"

    id:                      Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id:                 Mapped[int]   = mapped_column(ForeignKey("shipping_zones.id", ondelete="CASCADE"), nullable=False, index=True)
    shipping_fee:            Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    free_shipping_threshold: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active:               Mapped[bool]  = mapped_column(Boolean, default=True, nullable=False)

    zone:   Mapped["ShippingZone"]   = relationship(back_populates="rules")


# ── Logistics Carriers ────────────────────────────────────────────────────────
class LogisticsCarrier(Base, TimestampMixin):
    """UPS / FedEx / USPS etc."""
    __tablename__ = "logistics_carriers"

    id:                   Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:                 Mapped[str]           = mapped_column(String(100), nullable=False)
    code:                 Mapped[str]           = mapped_column(String(30), unique=True, nullable=False)
    tracking_url_template:Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # {tracking_no} placeholder
    applicable_countries: Mapped[Optional[list]]= mapped_column(JSON, nullable=True)          # null = all
    is_active:            Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)

    shipments: Mapped[list["Shipment"]] = relationship(back_populates="carrier")


# ── Shipments ─────────────────────────────────────────────────────────────────
class Shipment(Base):
    __tablename__ = "shipments"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id:    Mapped[int]           = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    carrier_id:  Mapped[int]           = mapped_column(ForeignKey("logistics_carriers.id", ondelete="RESTRICT"), nullable=False)
    tracking_no: Mapped[str]           = mapped_column(String(100), nullable=False)
    shipped_by:  Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    shipped_at:  Mapped[datetime]      = mapped_column(DateTime, server_default=func.now(), nullable=False)
    note:        Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    order:   Mapped["Order"]            = relationship(back_populates="shipment")
    carrier: Mapped["LogisticsCarrier"] = relationship(back_populates="shipments")


# ── Forward refs ──────────────────────────────────────────────────────────────
from app.models.order import Order   # noqa: E402
from app.models.admin import Admin   # noqa: E402
