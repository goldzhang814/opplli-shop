from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy import (
    String, Boolean, Text, Integer, Numeric, Float,
    ForeignKey, JSON, DateTime, func, SmallInteger, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin
import enum


class ReviewStatus(str, enum.Enum):
    pending  = "pending"
    approved = "approved"
    rejected = "rejected"


class MediaType(str, enum.Enum):
    image = "image"
    video = "video"


class StorageType(str, enum.Enum):
    local = "local"
    s3    = "s3"


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:        Mapped[str]           = mapped_column(String(100), nullable=False)
    slug:        Mapped[str]           = mapped_column(String(120), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id:   Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    sort_order:  Mapped[int]           = mapped_column(SmallInteger, default=0, nullable=False)
    is_active:   Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)

    parent:   Mapped[Optional["Category"]] = relationship("Category", remote_side="Category.id")
    products: Mapped[list["Product"]]      = relationship(back_populates="category")


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id:              Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:            Mapped[str]           = mapped_column(String(255), nullable=False)
    slug:            Mapped[str]           = mapped_column(String(191), unique=True, nullable=False, index=True)
    description:     Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    short_desc:      Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    category_id:     Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    is_published:    Mapped[bool]          = mapped_column(Boolean, default=False, nullable=False, index=True)
    rating_avg:      Mapped[float]         = mapped_column(Float, default=0.0, nullable=False)
    rating_count:    Mapped[int]           = mapped_column(Integer, default=0, nullable=False)
    # SEO
    seo_title:       Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    seo_slug:        Mapped[Optional[str]] = mapped_column(String(280), nullable=True)
    og_image:        Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    category:    Mapped[Optional["Category"]]    = relationship(back_populates="products")
    skus:        Mapped[list["ProductSku"]]       = relationship(back_populates="product", cascade="all, delete-orphan")
    images:      Mapped[list["ProductImage"]]     = relationship(back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.sort_order")
    reviews:     Mapped[list["ProductReview"]]    = relationship(back_populates="product")
    wishlist_items: Mapped[list["Wishlist"]]      = relationship(back_populates="product", cascade="all, delete-orphan")


class ProductSku(Base, TimestampMixin):
    __tablename__ = "product_skus"

    id:             Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id:     Mapped[int]            = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    sku_code:       Mapped[str]            = mapped_column(String(100), unique=True, nullable=False)
    price:          Mapped[float]          = mapped_column(Numeric(10, 2), nullable=False)
    compare_price:  Mapped[Optional[float]]= mapped_column(Numeric(10, 2), nullable=True)
    stock:          Mapped[int]            = mapped_column(Integer, default=0, nullable=False)
    low_stock_threshold: Mapped[int]       = mapped_column(Integer, default=5, nullable=False)
    variant_attrs:  Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)   # {"color": "red", "size": "M"}
    is_active:      Mapped[bool]           = mapped_column(Boolean, default=True, nullable=False)
    free_shipping:  Mapped[bool]           = mapped_column(Boolean, default=False, nullable=False)
    weight_grams:   Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)

    product:        Mapped["Product"]           = relationship(back_populates="skus")
    inventory_logs: Mapped[list["InventoryLog"]]= relationship(
        back_populates="sku",
        passive_deletes=True,
    )
    order_items:    Mapped[list["OrderItem"]]   = relationship(back_populates="sku")


class ProductImage(Base):
    __tablename__ = "product_images"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id:   Mapped[int]           = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    url:          Mapped[str]           = mapped_column(String(500), nullable=False)   # relative path or S3 key
    storage_type: Mapped[str]           = mapped_column(String(10), default="local", nullable=False)  # local | s3
    alt_text:     Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sort_order:   Mapped[int]           = mapped_column(SmallInteger, default=0, nullable=False)
    created_at:   Mapped[datetime]      = mapped_column(DateTime, server_default=func.now(), nullable=False)

    product: Mapped["Product"] = relationship(back_populates="images")


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku_id:       Mapped[int]           = mapped_column(ForeignKey("product_skus.id", ondelete="CASCADE"), nullable=False, index=True)
    change_qty:   Mapped[int]           = mapped_column(Integer, nullable=False)   # + or -
    before_qty:   Mapped[int]           = mapped_column(Integer, nullable=False)
    after_qty:    Mapped[int]           = mapped_column(Integer, nullable=False)
    reason:       Mapped[str]           = mapped_column(String(50), nullable=False)  # order|manual|return|adjustment
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # order_id or manual note
    operator_id:  Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    created_at:   Mapped[datetime]      = mapped_column(DateTime, server_default=func.now(), nullable=False)

    sku:      Mapped["ProductSku"]       = relationship(back_populates="inventory_logs")
    operator: Mapped[Optional["Admin"]]  = relationship()


class ProductReview(Base, TimestampMixin):
    __tablename__ = "product_reviews"

    id:             Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id:     Mapped[int]           = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id:        Mapped[int]           = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id:       Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    rating:         Mapped[int]           = mapped_column(SmallInteger, nullable=False)   # 1-5
    content:        Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status:         Mapped[str]           = mapped_column(String(20), default="pending", nullable=False, index=True)
    reject_reason:  Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reviewer_name:  Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_verified_purchase: Mapped[bool]    = mapped_column(Boolean, default=False, nullable=False)

    product: Mapped["Product"]              = relationship(back_populates="reviews")
    user:    Mapped["User"]                 = relationship(back_populates="reviews")
    media:   Mapped[list["ReviewMedia"]]    = relationship(back_populates="review", cascade="all, delete-orphan")


class ReviewMedia(Base):
    __tablename__ = "review_media"

    id:           Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_id:    Mapped[int]      = mapped_column(ForeignKey("product_reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    url:          Mapped[str]      = mapped_column(String(500), nullable=False)
    storage_type: Mapped[str]      = mapped_column(String(10), default="local", nullable=False)  # local | s3
    media_type:   Mapped[str]      = mapped_column(String(10), nullable=False)   # image | video
    sort_order:   Mapped[int]      = mapped_column(SmallInteger, default=0, nullable=False)
    created_at:   Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    review: Mapped["ProductReview"] = relationship(back_populates="media")


class Wishlist(Base):
    __tablename__ = "wishlist"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:    Mapped[int]      = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int]      = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user:    Mapped["User"]    = relationship(back_populates="wishlist_items")
    product: Mapped["Product"] = relationship(back_populates="wishlist_items")


# ── Forward refs ─────────────────────────────────────────────────────────────
from app.models.order import Order, OrderItem   # noqa: E402
from app.models.admin import Admin              # noqa: E402
