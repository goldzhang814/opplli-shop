from __future__ import annotations
from typing import Optional
from sqlalchemy import String, Integer, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


class TaxRule(Base, TimestampMixin):
    """
    Tax rules by country + optional state.
    apply_to_shipping: whether to tax shipping fee as well.
    """
    __tablename__ = "tax_rules"

    id:               Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    country_code:     Mapped[str]           = mapped_column(String(3), nullable=False, index=True)
    state_code:       Mapped[Optional[str]] = mapped_column(String(10), nullable=True)   # NULL = whole country
    tax_rate:         Mapped[float]         = mapped_column(Numeric(5, 4), nullable=False)  # e.g. 0.0825 = 8.25%
    tax_name:         Mapped[str]           = mapped_column(String(50), default="Sales Tax", nullable=False)
    apply_to_shipping:Mapped[bool]          = mapped_column(Boolean, default=False, nullable=False)
    category_id:      Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)  # per-category tax
    is_active:        Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)


# ── Forward refs ──────────────────────────────────────────────────────────────
from app.models.order import Order           # noqa: E402
