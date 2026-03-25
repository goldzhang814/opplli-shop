from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.base import TimestampMixin

# 18 permission modules
PERMISSION_MODULES = [
    "products", "categories", "inventory", "reviews",
    "orders", "payments", "coupons", "banners",
    "newsletter", "channels", "shipping", "tax",
    "carriers", "content", "seo", "email_templates",
    "statistics", "admins",
]

DEFAULT_PERMISSIONS: dict[str, bool] = {m: False for m in PERMISSION_MODULES}
SUPER_ADMIN_PERMISSIONS: dict[str, bool] = {m: True for m in PERMISSION_MODULES}


class Admin(Base, TimestampMixin):
    __tablename__ = "admins"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    email:         Mapped[str]           = mapped_column(String(191), unique=True, nullable=False, index=True)
    password_hash: Mapped[str]           = mapped_column(String(255), nullable=False)
    full_name:     Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role:          Mapped[str]           = mapped_column(String(20), default="admin", nullable=False)  # admin | super_admin
    is_active:     Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)
    permissions:   Mapped[dict]          = mapped_column(JSON, default=dict, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
