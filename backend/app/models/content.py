from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, Text, ForeignKey, DateTime, func, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin


# ── Blog ─────────────────────────────────────────────────────────────────────
class BlogCategory(Base, TimestampMixin):
    __tablename__ = "blog_categories"

    id:        Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:      Mapped[str]           = mapped_column(String(100), nullable=False)
    slug:      Mapped[str]           = mapped_column(String(120), unique=True, nullable=False, index=True)
    is_active: Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)

    posts: Mapped[list["BlogPost"]] = relationship(back_populates="category")


class BlogPost(Base, TimestampMixin):
    __tablename__ = "blog_posts"

    id:              Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    title:           Mapped[str]           = mapped_column(String(255), nullable=False)
    slug:            Mapped[str]           = mapped_column(String(191), unique=True, nullable=False, index=True)
    excerpt:         Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content:         Mapped[Optional[str]] = mapped_column(Text, nullable=True)           # rich text HTML
    author:          Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cover_storage_type: Mapped[str]        = mapped_column(String(10), default="local", nullable=False)
    category_id:     Mapped[Optional[int]] = mapped_column(ForeignKey("blog_categories.id", ondelete="SET NULL"), nullable=True)
    is_published:    Mapped[bool]          = mapped_column(Boolean, default=False, nullable=False, index=True)
    published_at:    Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # SEO
    seo_title:       Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    og_image:        Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    category: Mapped[Optional["BlogCategory"]] = relationship(back_populates="posts")


# ── FAQ ──────────────────────────────────────────────────────────────────────
class Faq(Base, TimestampMixin):
    __tablename__ = "faqs"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    question:      Mapped[str]           = mapped_column(Text, nullable=False)
    answer:        Mapped[str]           = mapped_column(Text, nullable=False)
    category:      Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sort_order:    Mapped[int]           = mapped_column(SmallInteger, default=0, nullable=False)
    language_code: Mapped[str]           = mapped_column(String(10), default="en", nullable=False)
    is_active:     Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)


# ── CMS Pages ────────────────────────────────────────────────────────────────
class CmsPage(Base, TimestampMixin):
    """
    page_type options:
      about_us | return_policy | shipping_policy |
      privacy_policy | terms_of_service | terms_of_use | cookie_policy
    """
    __tablename__ = "cms_pages"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    page_type:     Mapped[str]           = mapped_column(String(50), nullable=False, index=True)
    language_code: Mapped[str]           = mapped_column(String(10), default="en", nullable=False)
    title:         Mapped[str]           = mapped_column(String(255), nullable=False)
    content:       Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # rich text HTML
    is_published:  Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)


# ── Email Templates ───────────────────────────────────────────────────────────
class EmailTemplate(Base, TimestampMixin):
    """
    type options:
      order_confirmation | order_shipped | order_cancelled |
      order_refunded | payment_failed | password_reset
    Variables: {{order_id}} {{customer_name}} {{tracking_no}} etc.
    """
    __tablename__ = "email_templates"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    type:          Mapped[str]           = mapped_column(String(50), nullable=False, index=True)
    language_code: Mapped[str]           = mapped_column(String(10), default="en", nullable=False)
    subject:       Mapped[str]           = mapped_column(String(255), nullable=False)
    body:          Mapped[str]           = mapped_column(Text, nullable=False)   # HTML with {{variables}}
    is_active:     Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)


# ── Cookie Consent Config ─────────────────────────────────────────────────────
class CookieConsentConfig(Base, TimestampMixin):
    __tablename__ = "cookie_consent_configs"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    language_code: Mapped[str]           = mapped_column(String(10), default="en", nullable=False)
    title:         Mapped[str]           = mapped_column(String(255), nullable=False)
    description:   Mapped[str]           = mapped_column(Text, nullable=False)
    accept_btn:    Mapped[str]           = mapped_column(String(100), nullable=False)
    reject_btn:    Mapped[str]           = mapped_column(String(100), nullable=False)
    customize_btn: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active:     Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)


# ── Site Settings (key-value store) ──────────────────────────────────────────
class SiteSetting(Base, TimestampMixin):
    """
    Keys include: site_name, site_url, meta_title, meta_description,
    og_image, google_analytics_id, robots_txt, contact_whatsapp,
    contact_facebook, contact_telegram, contact_email,
    review_auto_approve_threshold (int, default 3, 0=all manual),
    etc.
    """
    __tablename__ = "site_settings"

    id:          Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    key:         Mapped[str]           = mapped_column("setting_key", String(100), unique=True, nullable=False, index=True)
    value:       Mapped[Optional[str]] = mapped_column("setting_value", Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


# ── Language Packs ────────────────────────────────────────────────────────────
class LanguagePack(Base, TimestampMixin):
    """Frontend i18n strings. language_code: en | es"""
    __tablename__ = "language_packs"

    id:            Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    language_code: Mapped[str]           = mapped_column(String(10), nullable=False, index=True)
    key:           Mapped[str]           = mapped_column("pack_key", String(200), nullable=False)
    value:         Mapped[str]           = mapped_column("pack_value", Text, nullable=False)


# ── Countries & States ────────────────────────────────────────────────────────
class Country(Base):
    __tablename__ = "countries"

    id:         Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:       Mapped[str]           = mapped_column(String(100), nullable=False)
    code:       Mapped[str]           = mapped_column(String(3), unique=True, nullable=False, index=True)
    is_active:  Mapped[bool]          = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int]           = mapped_column(SmallInteger, default=0, nullable=False)

    states: Mapped[list["CountryState"]] = relationship(back_populates="country")


class CountryState(Base):
    __tablename__ = "country_states"

    id:           Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    country_code: Mapped[str]  = mapped_column(ForeignKey("countries.code", ondelete="CASCADE"), nullable=False, index=True)
    name:         Mapped[str]  = mapped_column(String(100), nullable=False)
    code:         Mapped[str]  = mapped_column(String(10), nullable=False)
    is_active:    Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    country: Mapped["Country"] = relationship(back_populates="states")


# ── Media Files ────────────────────────────────────────────────────────────────
class MediaFile(Base, TimestampMixin):
    """
    Central media registry.
    storage_type field ensures correct URL resolution regardless of when the file was uploaded.
    - local: served from /media/{path} via Nginx
    - s3:    served from {CLOUDFLARE_CDN_URL}/{path}
    """
    __tablename__ = "media_files"

    id:           Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename:     Mapped[str]           = mapped_column(String(255), nullable=False)
    path:         Mapped[str]           = mapped_column(String(500), nullable=False)   # relative key/path
    storage_type: Mapped[str]           = mapped_column(String(10), nullable=False)    # local | s3
    file_type:    Mapped[str]           = mapped_column(String(20), nullable=False)    # image | video | document
    mime_type:    Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size_bytes:   Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    width:        Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height:       Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    uploaded_by:  Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)


# ── Forward refs ──────────────────────────────────────────────────────────────
from app.models.admin import Admin   # noqa: E402
