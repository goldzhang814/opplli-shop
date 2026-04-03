"""
Content Service
===============
Handles: Blog, FAQ, CMS pages, Email templates, Cookie consent,
         Site settings (key-value), Language packs, SEO,
         Newsletter subscriptions, Sitemap generation.
"""
from __future__ import annotations
import math
import secrets
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, update, delete, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import (
    BlogCategory, BlogPost, Faq, CmsPage,
    EmailTemplate, CookieConsentConfig,
    SiteSetting, LanguagePack, Country, CountryState,
)
from app.models.marketing import NewsletterSubscriber
from slugify import slugify


# ────────────────────────────────────────────────────────────────────────────
# Site Settings
# ────────────────────────────────────────────────────────────────────────────
async def get_setting(db: AsyncSession, key: str) -> Optional[str]:
    r = await db.execute(select(SiteSetting).where(SiteSetting.key == key))
    s = r.scalar_one_or_none()
    return s.value if s else None


async def get_settings_by_prefix(db: AsyncSession, prefix: str) -> dict[str, str]:
    r = await db.execute(
        select(SiteSetting).where(SiteSetting.key.like(f"{prefix}%"))
    )
    return {s.key: (s.value or "") for s in r.scalars().all()}


async def get_all_settings(db: AsyncSession) -> list[SiteSetting]:
    r = await db.execute(select(SiteSetting).order_by(SiteSetting.key))
    return r.scalars().all()


async def upsert_setting(db: AsyncSession, key: str, value: str) -> SiteSetting:
    r = await db.execute(select(SiteSetting).where(SiteSetting.key == key))
    s = r.scalar_one_or_none()
    if s:
        s.value = value
    else:
        s = SiteSetting(key=key, value=value)
        db.add(s)
    await db.flush()
    return s


async def bulk_upsert_settings(db: AsyncSession, data: dict[str, str]) -> None:
    for k, v in data.items():
        await upsert_setting(db, k, v)


async def get_settings_by_keys(db: AsyncSession, keys: list[str]) -> dict[str, str]:
    if not keys:
        return {}
    r = await db.execute(
        select(SiteSetting).where(SiteSetting.key.in_(keys))
    )
    return {s.key: (s.value or "") for s in r.scalars().all()}


# ────────────────────────────────────────────────────────────────────────────
# SEO config (stored as site_settings with seo.* prefix)
# ────────────────────────────────────────────────────────────────────────────
SEO_KEYS = [
    "meta_title", "meta_description", "og_image",
    "google_analytics_id", "robots_txt", "canonical_url",
]


async def get_seo_config(db: AsyncSession) -> dict[str, str]:
    settings: dict[str, str] = {}
    for key in SEO_KEYS:
        val = await get_setting(db, key)
        settings[key] = val or ""
    return settings


async def update_seo_config(db: AsyncSession, data: dict[str, str]) -> dict[str, str]:
    for key in SEO_KEYS:
        if key in data:
            await upsert_setting(db, key, data[key])
    return await get_seo_config(db)


# ────────────────────────────────────────────────────────────────────────────
# Language packs
# ────────────────────────────────────────────────────────────────────────────
async def get_language_pack(db: AsyncSession, lang: str) -> dict[str, str]:
    r = await db.execute(
        select(LanguagePack).where(LanguagePack.language_code == lang)
    )
    return {row.key: row.value for row in r.scalars().all()}


async def upsert_lang_key(
    db: AsyncSession, lang: str, key: str, value: str
) -> LanguagePack:
    r = await db.execute(
        select(LanguagePack).where(
            LanguagePack.language_code == lang,
            LanguagePack.key           == key,
        )
    )
    lp = r.scalar_one_or_none()
    if lp:
        lp.value = value
    else:
        lp = LanguagePack(language_code=lang, key=key, value=value)
        db.add(lp)
    await db.flush()
    return lp


async def bulk_upsert_lang(db: AsyncSession, lang: str, data: dict[str, str]) -> None:
    for k, v in data.items():
        await upsert_lang_key(db, lang, k, v)


# ────────────────────────────────────────────────────────────────────────────
# Blog Categories
# ────────────────────────────────────────────────────────────────────────────
async def list_blog_categories(db: AsyncSession, active_only: bool = True) -> list[BlogCategory]:
    q = select(BlogCategory).order_by(BlogCategory.name)
    if active_only:
        q = q.where(BlogCategory.is_active == True)
    return (await db.execute(q)).scalars().all()


async def create_blog_category(db: AsyncSession, name: str, slug: Optional[str] = None) -> BlogCategory:
    s = slugify(slug or name)
    cat = BlogCategory(name=name, slug=s)
    db.add(cat)
    await db.flush()
    return cat


# ────────────────────────────────────────────────────────────────────────────
# Blog Posts
# ────────────────────────────────────────────────────────────────────────────
async def _unique_blog_slug(db: AsyncSession, base: str, exclude_id: Optional[int] = None) -> str:
    slug = slugify(base)
    q    = select(BlogPost).where(BlogPost.slug == slug)
    if exclude_id:
        q = q.where(BlogPost.id != exclude_id)
    if not (await db.execute(q)).scalar_one_or_none():
        return slug
    c = 1
    while True:
        candidate = f"{slug}-{c}"
        q2 = select(BlogPost).where(BlogPost.slug == candidate)
        if exclude_id:
            q2 = q2.where(BlogPost.id != exclude_id)
        if not (await db.execute(q2)).scalar_one_or_none():
            return candidate
        c += 1


async def list_blog_posts(
    db:           AsyncSession,
    page:         int           = 1,
    limit:        int           = 10,
    category_id:  Optional[int] = None,
    published_only: bool        = True,
) -> dict:
    #q = select(BlogPost).order_by(BlogPost.published_at.desc().nullslast())
    q = select(BlogPost).order_by(BlogPost.published_at.desc())
    if published_only:
        q = q.where(BlogPost.is_published == True)
    if category_id:
        q = q.where(BlogPost.category_id == category_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {
        "items": items, "total": total, "page": page,
        "pages": max(1, math.ceil(total / limit)),
    }


async def get_blog_post_by_slug(db: AsyncSession, slug: str, published_only: bool = True) -> BlogPost:
    q = select(BlogPost).where(BlogPost.slug == slug)
    if published_only:
        q = q.where(BlogPost.is_published == True)
    post = (await db.execute(q)).scalar_one_or_none()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Blog post not found")
    return post


async def create_blog_post(db: AsyncSession, data: dict) -> BlogPost:
    slug = await _unique_blog_slug(db, data.get("slug") or data.get("title", "post"))
    post = BlogPost(**{k: v for k, v in data.items() if k != "slug"}, slug=slug)
    if post.is_published and not post.published_at:
        post.published_at = datetime.now(timezone.utc)
    db.add(post)
    await db.flush()
    return post


async def update_blog_post(db: AsyncSession, post_id: int, data: dict) -> BlogPost:
    r    = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = r.scalar_one_or_none()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Blog post not found")
    if "slug" in data and data["slug"] != post.slug:
        data["slug"] = await _unique_blog_slug(db, data["slug"], exclude_id=post_id)
    for k, v in data.items():
        setattr(post, k, v)
    if post.is_published and not post.published_at:
        post.published_at = datetime.now(timezone.utc)
    return post


async def delete_blog_post(db: AsyncSession, post_id: int) -> None:
    r    = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = r.scalar_one_or_none()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Blog post not found")
    await db.delete(post)


# ────────────────────────────────────────────────────────────────────────────
# FAQ
# ────────────────────────────────────────────────────────────────────────────
async def list_faqs(
    db:        AsyncSession,
    lang:      str           = "en",
    category:  Optional[str] = None,
    active_only: bool        = True,
) -> list[Faq]:
    q = select(Faq).where(Faq.language_code == lang)
    if active_only:
        q = q.where(Faq.is_active == True)
    if category:
        q = q.where(Faq.category == category)
    q = q.order_by(Faq.sort_order, Faq.id)
    return (await db.execute(q)).scalars().all()


async def create_faq(db: AsyncSession, data: dict) -> Faq:
    faq = Faq(**data)
    db.add(faq)
    await db.flush()
    return faq


async def update_faq(db: AsyncSession, faq_id: int, data: dict) -> Faq:
    r   = await db.execute(select(Faq).where(Faq.id == faq_id))
    faq = r.scalar_one_or_none()
    if not faq:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "FAQ not found")
    for k, v in data.items():
        setattr(faq, k, v)
    return faq


async def delete_faq(db: AsyncSession, faq_id: int) -> None:
    r   = await db.execute(select(Faq).where(Faq.id == faq_id))
    faq = r.scalar_one_or_none()
    if not faq:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "FAQ not found")
    await db.delete(faq)


async def faq_categories(db: AsyncSession, lang: str = "en") -> list[str]:
    r = await db.execute(
        select(Faq.category).where(
            Faq.language_code == lang,
            Faq.is_active     == True,
            Faq.category      != None,
        ).distinct()
    )
    return [row[0] for row in r.all() if row[0]]


# ────────────────────────────────────────────────────────────────────────────
# CMS Pages
# ────────────────────────────────────────────────────────────────────────────
CMS_PAGE_TYPES = [
    "about_us", "return_policy", "shipping_policy",
    "privacy_policy", "terms_of_service", "terms_of_use", "cookie_policy",
]


async def get_cms_page(
    db:        AsyncSession,
    page_type: str,
    lang:      str = "en",
) -> Optional[CmsPage]:
    # Try requested language first, fall back to English
    r = await db.execute(
        select(CmsPage).where(
            CmsPage.page_type     == page_type,
            CmsPage.language_code == lang,
            CmsPage.is_published  == True,
        )
    )
    page = r.scalar_one_or_none()
    if not page and lang != "en":
        r2 = await db.execute(
            select(CmsPage).where(
                CmsPage.page_type     == page_type,
                CmsPage.language_code == "en",
                CmsPage.is_published  == True,
            )
        )
        page = r2.scalar_one_or_none()
    return page


async def upsert_cms_page(
    db:        AsyncSession,
    page_type: str,
    lang:      str,
    title:     str,
    content:   str,
) -> CmsPage:
    r    = await db.execute(
        select(CmsPage).where(
            CmsPage.page_type     == page_type,
            CmsPage.language_code == lang,
        )
    )
    page = r.scalar_one_or_none()
    if page:
        page.title   = title
        page.content = content
    else:
        page = CmsPage(
            page_type     = page_type,
            language_code = lang,
            title         = title,
            content       = content,
            is_published  = True,
        )
        db.add(page)
    await db.flush()
    return page


async def list_cms_pages(db: AsyncSession) -> list[CmsPage]:
    r = await db.execute(select(CmsPage).order_by(CmsPage.page_type, CmsPage.language_code))
    return r.scalars().all()


# ────────────────────────────────────────────────────────────────────────────
# Email Templates
# ────────────────────────────────────────────────────────────────────────────
async def list_email_templates(db: AsyncSession) -> list[EmailTemplate]:
    r = await db.execute(
        select(EmailTemplate).order_by(EmailTemplate.type, EmailTemplate.language_code)
    )
    return r.scalars().all()


async def upsert_email_template(
    db:   AsyncSession,
    ttype: str,
    lang:  str,
    subject: str,
    body:    str,
) -> EmailTemplate:
    r    = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.type          == ttype,
            EmailTemplate.language_code == lang,
        )
    )
    tmpl = r.scalar_one_or_none()
    if tmpl:
        tmpl.subject = subject
        tmpl.body    = body
    else:
        tmpl = EmailTemplate(
            type          = ttype,
            language_code = lang,
            subject       = subject,
            body          = body,
            is_active     = True,
        )
        db.add(tmpl)
    await db.flush()
    return tmpl


async def send_test_email(db: AsyncSession, template_type: str, lang: str, to_email: str) -> None:
    """Send a test email using the stored template with placeholder values."""
    r    = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.type          == template_type,
            EmailTemplate.language_code == lang,
            EmailTemplate.is_active     == True,
        )
    )
    tmpl = r.scalar_one_or_none()
    if not tmpl:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")

    # Fill placeholders with test values
    test_vars = {
        "order_id":       "TEST-001",
        "customer_name":  "Test Customer",
        "carrier_name":   "UPS",
        "tracking_no":    "1Z999AA10123456784",
        "tracking_url":   "https://ups.com/track",
        "refund_amount":  "25.00",
        "fail_reason":    "Insufficient funds",
        "retry_url":      "https://example.com/retry",
        "reset_url":      "https://example.com/reset",
    }

    def _render(text: str) -> str:
        for k, v in test_vars.items():
            text = text.replace(f"{{{{{k}}}}}", v)
        return text

    from app.tasks.email_tasks import _send_email
    _send_email(to_email, f"[TEST] {_render(tmpl.subject)}", _render(tmpl.body))


# ────────────────────────────────────────────────────────────────────────────
# Cookie consent config
# ────────────────────────────────────────────────────────────────────────────
async def get_cookie_config(db: AsyncSession, lang: str = "en") -> Optional[CookieConsentConfig]:
    r = await db.execute(
        select(CookieConsentConfig).where(
            CookieConsentConfig.language_code == lang,
            CookieConsentConfig.is_active     == True,
        )
    )
    cfg = r.scalar_one_or_none()
    if not cfg and lang != "en":
        r2 = await db.execute(
            select(CookieConsentConfig).where(
                CookieConsentConfig.language_code == "en",
                CookieConsentConfig.is_active     == True,
            )
        )
        cfg = r2.scalar_one_or_none()
    return cfg


async def upsert_cookie_config(db: AsyncSession, lang: str, data: dict) -> CookieConsentConfig:
    r   = await db.execute(
        select(CookieConsentConfig).where(CookieConsentConfig.language_code == lang)
    )
    cfg = r.scalar_one_or_none()
    if cfg:
        for k, v in data.items():
            setattr(cfg, k, v)
    else:
        cfg = CookieConsentConfig(language_code=lang, **data)
        db.add(cfg)
    await db.flush()
    return cfg


# ────────────────────────────────────────────────────────────────────────────
# Newsletter
# ────────────────────────────────────────────────────────────────────────────
async def subscribe_newsletter(
    db:     AsyncSession,
    email:  str,
    source: str = "footer",
    lang:   str = "en",
) -> dict:
    r    = await db.execute(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
    )
    sub  = r.scalar_one_or_none()

    if sub:
        if sub.status == "active":
            return {"status": "already_subscribed"}
        # Re-subscribe
        sub.status          = "active"
        sub.unsubscribed_at = None
        sub.source          = source
        return {"status": "resubscribed"}

    token = secrets.token_urlsafe(32)
    sub   = NewsletterSubscriber(
        email         = email,
        source        = source,
        status        = "active",
        language_code = lang,
        unsub_token   = token,
    )
    db.add(sub)
    await db.flush()
    return {"status": "subscribed"}


async def unsubscribe_newsletter(db: AsyncSession, token: str) -> dict:
    r   = await db.execute(
        select(NewsletterSubscriber).where(NewsletterSubscriber.unsub_token == token)
    )
    sub = r.scalar_one_or_none()
    if not sub:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Token not found")
    sub.status          = "unsubscribed"
    sub.unsubscribed_at = datetime.now(timezone.utc)
    return {"status": "unsubscribed", "email": sub.email}


async def list_subscribers(
    db:     AsyncSession,
    page:   int           = 1,
    limit:  int           = 50,
    status_f: Optional[str] = None,
    source: Optional[str] = None,
) -> dict:
    q = select(NewsletterSubscriber).order_by(NewsletterSubscriber.subscribed_at.desc())
    if status_f:
        q = q.where(NewsletterSubscriber.status == status_f)
    if source:
        q = q.where(NewsletterSubscriber.source == source)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {
        "items": items, "total": total, "page": page,
        "pages": max(1, math.ceil(total / limit)),
    }


async def newsletter_stats(db: AsyncSession) -> dict:
    r = await db.execute(
        select(
            func.count().label("total"),
            func.sum(
                func.if_(NewsletterSubscriber.status == "active", 1, 0)
            ).label("active"),
            func.sum(
                func.if_(NewsletterSubscriber.status == "unsubscribed", 1, 0)
            ).label("unsubscribed"),
        )
    )
    row = r.one()
    return {
        "total":        row.total or 0,
        "active":       int(row.active or 0),
        "unsubscribed": int(row.unsubscribed or 0),
    }


async def export_subscribers_csv(db: AsyncSession) -> str:
    r    = await db.execute(
        select(NewsletterSubscriber)
        .where(NewsletterSubscriber.status == "active")
        .order_by(NewsletterSubscriber.subscribed_at.desc())
    )
    subs = r.scalars().all()

    lines = ["email,source,language,subscribed_at"]
    for s in subs:
        lines.append(
            f"{s.email},{s.source},{s.language_code},"
            f"{s.subscribed_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    return "\n".join(lines)


async def remove_subscriber(db: AsyncSession, subscriber_id: int) -> None:
    r   = await db.execute(select(NewsletterSubscriber).where(NewsletterSubscriber.id == subscriber_id))
    sub = r.scalar_one_or_none()
    if not sub:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subscriber not found")
    await db.delete(sub)


# ────────────────────────────────────────────────────────────────────────────
# Banners + Coupons (marketing)
# ────────────────────────────────────────────────────────────────────────────
async def get_active_banners(db: AsyncSession) -> list:
    from app.models.marketing import Banner
    now = datetime.now(timezone.utc)
    q   = (
        select(Banner)
        .where(
            Banner.is_active == True,
            or_(Banner.starts_at == None, Banner.starts_at <= now),
            or_(Banner.ends_at   == None, Banner.ends_at   >= now),
        )
        .order_by(Banner.sort_order)
    )
    return (await db.execute(q)).scalars().all()


async def list_banners(db: AsyncSession) -> list:
    from app.models.marketing import Banner
    r = await db.execute(select(Banner).order_by(Banner.sort_order, Banner.id))
    return r.scalars().all()


async def create_banner(db: AsyncSession, data: dict) -> object:
    from app.models.marketing import Banner
    b = Banner(**data)
    db.add(b)
    await db.flush()
    return b


async def update_banner(db: AsyncSession, banner_id: int, data: dict) -> object:
    from app.models.marketing import Banner
    r = await db.execute(select(Banner).where(Banner.id == banner_id))
    b = r.scalar_one_or_none()
    if not b:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Banner not found")
    for k, v in data.items():
        setattr(b, k, v)
    return b


async def delete_banner(db: AsyncSession, banner_id: int) -> None:
    from app.models.marketing import Banner
    r = await db.execute(select(Banner).where(Banner.id == banner_id))
    b = r.scalar_one_or_none()
    if not b:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Banner not found")
    await db.delete(b)


# ────────────────────────────────────────────────────────────────────────────
# Marketing Channels
# ────────────────────────────────────────────────────────────────────────────
async def list_channels(db: AsyncSession) -> list:
    from app.models.marketing import MarketingChannel
    r = await db.execute(select(MarketingChannel).order_by(MarketingChannel.name))
    return r.scalars().all()


async def create_channel(db: AsyncSession, data: dict) -> object:
    from app.models.marketing import MarketingChannel
    ch = MarketingChannel(**data)
    db.add(ch)
    await db.flush()
    return ch


async def update_channel(db: AsyncSession, channel_id: int, data: dict) -> object:
    from app.models.marketing import MarketingChannel
    r  = await db.execute(select(MarketingChannel).where(MarketingChannel.id == channel_id))
    ch = r.scalar_one_or_none()
    if not ch:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Channel not found")
    for k, v in data.items():
        setattr(ch, k, v)
    return ch


async def channel_stats(db: AsyncSession, channel_id: int) -> dict:
    from app.models.marketing import ChannelEvent
    from app.models.order import Order
    from sqlalchemy import and_

    # Event counts per type
    r = await db.execute(
        select(ChannelEvent.event_type, func.count().label("cnt"))
        .where(ChannelEvent.channel_id == channel_id)
        .group_by(ChannelEvent.event_type)
    )
    counts = {row.event_type: row.cnt for row in r.all()}

    # Revenue from orders
    r2 = await db.execute(
        select(func.sum(Order.total_amount), func.count(Order.id))
        .where(
            Order.channel_id == channel_id,
            Order.payment_status == "paid",
        )
    )
    rev_row = r2.one()
    return {
        "channel_id":       channel_id,
        "visit_count":      counts.get("visit", 0),
        "add_to_cart_count":counts.get("add_to_cart", 0),
        "order_count":      counts.get("order", 0),
        "total_revenue":    float(rev_row[0] or 0),
        "paid_orders":      rev_row[1] or 0,
    }


# ────────────────────────────────────────────────────────────────────────────
# Sitemap
# ────────────────────────────────────────────────────────────────────────────
async def generate_sitemap(db: AsyncSession, base_url: str) -> str:
    from app.models.product import Product

    urls: list[dict] = [
        {"loc": base_url, "priority": "1.0", "changefreq": "daily"},
        {"loc": f"{base_url}/products", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{base_url}/blog",     "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{base_url}/faq",      "priority": "0.7", "changefreq": "monthly"},
    ]

    # CMS pages
    for pt in ["about_us", "return_policy", "shipping_policy",
               "privacy_policy", "terms_of_service", "terms_of_use"]:
        urls.append({"loc": f"{base_url}/pages/{pt.replace('_', '-')}", "priority": "0.5"})

    # Products
    r = await db.execute(
        select(Product.slug, Product.updated_at)
        .where(Product.is_published == True)
    )
    for slug, updated in r.all():
        urls.append({
            "loc":      f"{base_url}/products/{slug}",
            "lastmod":  updated.strftime("%Y-%m-%d") if updated else None,
            "priority": "0.8",
            "changefreq": "weekly",
        })

    # Blog posts
    r2 = await db.execute(
        select(BlogPost.slug, BlogPost.published_at)
        .where(BlogPost.is_published == True)
    )
    for slug, pub_at in r2.all():
        urls.append({
            "loc":      f"{base_url}/blog/{slug}",
            "lastmod":  pub_at.strftime("%Y-%m-%d") if pub_at else None,
            "priority": "0.7",
            "changefreq": "monthly",
        })

    # Build XML
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append("  <url>")
        lines.append(f'    <loc>{u["loc"]}</loc>')
        if u.get("lastmod"):
            lines.append(f'    <lastmod>{u["lastmod"]}</lastmod>')
        if u.get("changefreq"):
            lines.append(f'    <changefreq>{u["changefreq"]}</changefreq>')
        if u.get("priority"):
            lines.append(f'    <priority>{u["priority"]}</priority>')
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines)
