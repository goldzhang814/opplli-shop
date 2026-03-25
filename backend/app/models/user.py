from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Boolean, Text, DateTime, ForeignKey,
    Integer, func, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin
import enum


class UserRole(str, enum.Enum):
    customer = "customer"
    admin    = "admin"


class OAuthProvider(str, enum.Enum):
    google   = "google"
    facebook = "facebook"
    apple    = "apple"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    email:         Mapped[str]           = mapped_column(String(191), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)   # null for OAuth-only
    full_name:     Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone:         Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    language_code: Mapped[str]           = mapped_column(String(10), default="en", nullable=False)
    role:          Mapped[str]           = mapped_column(String(20), default="customer", nullable=False)
    is_guest:      Mapped[bool]          = mapped_column(Boolean, default=False, nullable=False)
    is_active:     Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)
    agree_terms:   Mapped[bool]          = mapped_column(Boolean, default=False, nullable=False)
    agreed_at:     Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    avatar_url:    Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    addresses:      Mapped[list["UserAddress"]]   = relationship(back_populates="user", cascade="all, delete-orphan")
    oauth_accounts: Mapped[list["OAuthAccount"]]  = relationship(back_populates="user", cascade="all, delete-orphan")
    wishlist_items: Mapped[list["Wishlist"]]       = relationship(back_populates="user", cascade="all, delete-orphan")
    reviews:        Mapped[list["ProductReview"]]  = relationship(back_populates="user")
    orders:         Mapped[list["Order"]]          = relationship(back_populates="user")


class UserAddress(Base, TimestampMixin):
    __tablename__ = "user_addresses"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:       Mapped[int]           = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    full_name:     Mapped[str]           = mapped_column(String(100), nullable=False)
    phone:         Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    country_code:  Mapped[str]           = mapped_column(String(3), nullable=False)
    state_code:    Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    state_name:    Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city:          Mapped[str]           = mapped_column(String(100), nullable=False)
    address_line1: Mapped[str]           = mapped_column(String(255), nullable=False)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    postal_code:   Mapped[str]           = mapped_column(String(20), nullable=False)
    is_default:    Mapped[bool]          = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="addresses")


class OAuthAccount(Base, TimestampMixin):
    __tablename__ = "oauth_accounts"

    id:               Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:          Mapped[int]           = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider:         Mapped[str]           = mapped_column(String(20), nullable=False)   # google|facebook|apple
    provider_user_id: Mapped[str]           = mapped_column(String(255), nullable=False)
    access_token:     Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token:    Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="oauth_accounts")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:    Mapped[int]      = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token:      Mapped[str]      = mapped_column(String(191), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used:       Mapped[bool]     = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class GuestClaimToken(Base):
    __tablename__ = "guest_claim_tokens"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:    Mapped[int]      = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token:      Mapped[str]      = mapped_column(String(191), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used:       Mapped[bool]     = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


# ── Import forward refs ──────────────────────────────────────────────────────
from app.models.product import Wishlist, ProductReview  # noqa: E402
from app.models.order import Order                       # noqa: E402
