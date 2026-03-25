"""
Admin Content Router
====================
Blog:
  GET/POST/PUT/DELETE  /api/v1/admin/blog
  GET/POST/PUT/DELETE  /api/v1/admin/blog/categories

FAQ:
  GET/POST/PUT/DELETE  /api/v1/admin/faq

CMS:
  GET/PUT              /api/v1/admin/cms/{page_type}/{lang}

Email Templates:
  GET/PUT              /api/v1/admin/email-templates
  POST                 /api/v1/admin/email-templates/test

Cookie:
  GET/PUT              /api/v1/admin/cookie-consent/{lang}

Settings:
  GET/PUT              /api/v1/admin/settings
  GET/PUT              /api/v1/admin/seo

Language Packs:
  GET/PUT              /api/v1/admin/i18n/{lang}

Newsletter:
  GET/DELETE           /api/v1/admin/newsletter
  GET                  /api/v1/admin/newsletter/stats
  GET                  /api/v1/admin/newsletter/export

Banners:
  GET/POST/PUT/DELETE  /api/v1/admin/banners

Coupons:
  GET/POST/PUT/DELETE  /api/v1/admin/coupons

Channels:
  GET/POST/PUT         /api/v1/admin/channels
  GET                  /api/v1/admin/channels/{id}/stats

Dashboard:
  GET                  /api/v1/admin/dashboard
"""
from typing import Optional, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.core.dependencies import require_permission, get_current_admin
from app.models.admin import Admin
from app.services import content_service

router = APIRouter(prefix="/admin", tags=["Admin — Content & Marketing"])


# ── Blog categories ───────────────────────────────────────────────────────────
@router.get("/blog/categories")
async def admin_blog_categories(
    _:  Admin        = Depends(require_permission("content")),
    db: AsyncSession = Depends(get_db),
):
    return await content_service.list_blog_categories(db, active_only=False)


class BlogCategoryCreate(BaseModel):
    name: str
    slug: Optional[str] = None


@router.post("/blog/categories", status_code=201)
async def admin_create_blog_category(
    req: BlogCategoryCreate,
    _:   Admin        = Depends(require_permission("content")),
    db:  AsyncSession = Depends(get_db),
):
    return await content_service.create_blog_category(db, req.name, req.slug)


# ── Blog posts ────────────────────────────────────────────────────────────────
@router.get("/blog")
async def admin_list_blog(
    page:  int          = Query(1, ge=1),
    limit: int          = Query(20, ge=1, le=100),
    _:     Admin        = Depends(require_permission("content")),
    db:    AsyncSession = Depends(get_db),
):
    return await content_service.list_blog_posts(db, page=page, limit=limit, published_only=False)


class BlogPostCreate(BaseModel):
    title:           str
    slug:            Optional[str]  = None
    excerpt:         Optional[str]  = None
    content:         Optional[str]  = None
    author:          Optional[str]  = None
    category_id:     Optional[int]  = None
    is_published:    bool           = False
    seo_title:       Optional[str]  = None
    seo_description: Optional[str]  = None


class BlogPostUpdate(BlogPostCreate):
    title: Optional[str] = None


@router.post("/blog", status_code=201)
async def admin_create_blog(
    req: BlogPostCreate,
    _:   Admin        = Depends(require_permission("content")),
    db:  AsyncSession = Depends(get_db),
):
    return await content_service.create_blog_post(db, req.model_dump())


@router.put("/blog/{post_id}")
async def admin_update_blog(
    post_id: int,
    req:     BlogPostUpdate,
    _:       Admin        = Depends(require_permission("content")),
    db:      AsyncSession = Depends(get_db),
):
    return await content_service.update_blog_post(db, post_id, req.model_dump(exclude_none=True))


@router.delete("/blog/{post_id}", status_code=204)
async def admin_delete_blog(
    post_id: int,
    _:       Admin        = Depends(require_permission("content")),
    db:      AsyncSession = Depends(get_db),
):
    await content_service.delete_blog_post(db, post_id)


# ── FAQ ───────────────────────────────────────────────────────────────────────
@router.get("/faq")
async def admin_list_faq(
    lang:      str          = "en",
    _:         Admin        = Depends(require_permission("content")),
    db:        AsyncSession = Depends(get_db),
):
    return await content_service.list_faqs(db, lang=lang, active_only=False)


class FaqCreate(BaseModel):
    question:      str
    answer:        str
    category:      Optional[str] = None
    sort_order:    int           = 0
    language_code: str           = "en"
    is_active:     bool          = True


class FaqUpdate(BaseModel):
    question:      Optional[str]  = None
    answer:        Optional[str]  = None
    category:      Optional[str]  = None
    sort_order:    Optional[int]  = None
    language_code: Optional[str]  = None
    is_active:     Optional[bool] = None


@router.post("/faq", status_code=201)
async def admin_create_faq(
    req: FaqCreate,
    _:   Admin        = Depends(require_permission("content")),
    db:  AsyncSession = Depends(get_db),
):
    return await content_service.create_faq(db, req.model_dump())


@router.put("/faq/{faq_id}")
async def admin_update_faq(
    faq_id: int,
    req:    FaqUpdate,
    _:      Admin        = Depends(require_permission("content")),
    db:     AsyncSession = Depends(get_db),
):
    return await content_service.update_faq(db, faq_id, req.model_dump(exclude_none=True))


@router.delete("/faq/{faq_id}", status_code=204)
async def admin_delete_faq(
    faq_id: int,
    _:      Admin        = Depends(require_permission("content")),
    db:     AsyncSession = Depends(get_db),
):
    await content_service.delete_faq(db, faq_id)


# ── CMS Pages ─────────────────────────────────────────────────────────────────
@router.get("/cms")
async def admin_list_cms(
    _:  Admin        = Depends(require_permission("content")),
    db: AsyncSession = Depends(get_db),
):
    return await content_service.list_cms_pages(db)


class CmsPageUpdate(BaseModel):
    title:   str
    content: str


@router.put("/cms/{page_type}/{lang}")
async def admin_update_cms(
    page_type: str,
    lang:      str,
    req:       CmsPageUpdate,
    _:         Admin        = Depends(require_permission("content")),
    db:        AsyncSession = Depends(get_db),
):
    return await content_service.upsert_cms_page(db, page_type, lang, req.title, req.content)


# ── Email Templates ───────────────────────────────────────────────────────────
@router.get("/email-templates")
async def admin_list_email_templates(
    _:  Admin        = Depends(require_permission("email_templates")),
    db: AsyncSession = Depends(get_db),
):
    return await content_service.list_email_templates(db)


class EmailTemplateUpdate(BaseModel):
    subject: str
    body:    str


@router.put("/email-templates/{ttype}/{lang}")
async def admin_update_email_template(
    ttype: str,
    lang:  str,
    req:   EmailTemplateUpdate,
    _:     Admin        = Depends(require_permission("email_templates")),
    db:    AsyncSession = Depends(get_db),
):
    return await content_service.upsert_email_template(db, ttype, lang, req.subject, req.body)


class TestEmailRequest(BaseModel):
    template_type: str
    lang:          str = "en"
    to_email:      EmailStr


@router.post("/email-templates/test", status_code=204)
async def admin_send_test_email(
    req: TestEmailRequest,
    _:   Admin        = Depends(require_permission("email_templates")),
    db:  AsyncSession = Depends(get_db),
):
    await content_service.send_test_email(db, req.template_type, req.lang, req.to_email)


# ── Cookie consent ────────────────────────────────────────────────────────────
class CookieConfigUpdate(BaseModel):
    title:         str
    description:   str
    accept_btn:    str
    reject_btn:    str
    customize_btn: Optional[str] = None
    is_active:     bool          = True


@router.get("/cookie-consent")
async def admin_list_cookie_configs(
    _:  Admin        = Depends(require_permission("content")),
    db: AsyncSession = Depends(get_db),
):
    from app.models.content import CookieConsentConfig
    r = await db.execute(select(CookieConsentConfig))
    return r.scalars().all()


@router.put("/cookie-consent/{lang}")
async def admin_update_cookie_config(
    lang: str,
    req:  CookieConfigUpdate,
    _:    Admin        = Depends(require_permission("content")),
    db:   AsyncSession = Depends(get_db),
):
    return await content_service.upsert_cookie_config(db, lang, req.model_dump())


# ── Site Settings ─────────────────────────────────────────────────────────────
@router.get("/settings")
async def admin_get_settings(
    _:  Admin        = Depends(require_permission("settings")),
    db: AsyncSession = Depends(get_db),
):
    return await content_service.get_all_settings(db)


class SettingUpdate(BaseModel):
    value: str


@router.put("/settings/{key}")
async def admin_update_setting(
    key: str,
    req: SettingUpdate,
    _:   Admin        = Depends(require_permission("settings")),
    db:  AsyncSession = Depends(get_db),
):
    return await content_service.upsert_setting(db, key, req.value)


# ── SEO Config ────────────────────────────────────────────────────────────────
@router.get("/seo")
async def admin_get_seo(
    _:  Admin        = Depends(require_permission("seo")),
    db: AsyncSession = Depends(get_db),
):
    return await content_service.get_seo_config(db)


@router.put("/seo")
async def admin_update_seo(
    data: dict[str, str],
    _:    Admin        = Depends(require_permission("seo")),
    db:   AsyncSession = Depends(get_db),
):
    return await content_service.update_seo_config(db, data)


# ── Language Packs ────────────────────────────────────────────────────────────
@router.get("/i18n/{lang}")
async def admin_get_lang_pack(
    lang: str,
    _:    Admin        = Depends(require_permission("content")),
    db:   AsyncSession = Depends(get_db),
):
    return await content_service.get_language_pack(db, lang)


@router.put("/i18n/{lang}")
async def admin_update_lang_pack(
    lang: str,
    data: dict[str, str],
    _:    Admin        = Depends(require_permission("content")),
    db:   AsyncSession = Depends(get_db),
):
    await content_service.bulk_upsert_lang(db, lang, data)
    return {"status": "updated", "keys": len(data)}


# ── Newsletter ────────────────────────────────────────────────────────────────
@router.get("/newsletter")
async def admin_list_newsletter(
    page:   int           = Query(1, ge=1),
    status: Optional[str] = None,
    source: Optional[str] = None,
    _:      Admin         = Depends(require_permission("newsletter")),
    db:     AsyncSession  = Depends(get_db),
):
    return await content_service.list_subscribers(
        db, page=page, status_f=status, source=source
    )


@router.get("/newsletter/stats")
async def admin_newsletter_stats(
    _:  Admin        = Depends(require_permission("newsletter")),
    db: AsyncSession = Depends(get_db),
):
    return await content_service.newsletter_stats(db)


@router.get("/newsletter/export", response_class=PlainTextResponse)
async def admin_newsletter_export(
    _:  Admin        = Depends(require_permission("newsletter")),
    db: AsyncSession = Depends(get_db),
):
    from fastapi.responses import Response
    csv_data = await content_service.export_subscribers_csv(db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=subscribers.csv"},
    )


@router.delete("/newsletter/{subscriber_id}", status_code=204)
async def admin_remove_subscriber(
    subscriber_id: int,
    _:             Admin        = Depends(require_permission("newsletter")),
    db:            AsyncSession = Depends(get_db),
):
    await content_service.remove_subscriber(db, subscriber_id)


# ── Banners ───────────────────────────────────────────────────────────────────
@router.get("/banners")
async def admin_list_banners(
    _:  Admin        = Depends(require_permission("banners")),
    db: AsyncSession = Depends(get_db),
):
    return await content_service.list_banners(db)


class BannerCreate(BaseModel):
    title:      str
    subtitle:   Optional[str]      = None
    coupon_id:  Optional[int]      = None
    link_url:   Optional[str]      = None
    starts_at:  Optional[datetime] = None
    ends_at:    Optional[datetime] = None
    is_active:  bool               = True
    sort_order: int                = 0


class BannerUpdate(BaseModel):
    title:      Optional[str]      = None
    subtitle:   Optional[str]      = None
    coupon_id:  Optional[int]      = None
    link_url:   Optional[str]      = None
    starts_at:  Optional[datetime] = None
    ends_at:    Optional[datetime] = None
    is_active:  Optional[bool]     = None
    sort_order: Optional[int]      = None


@router.post("/banners", status_code=201)
async def admin_create_banner(
    req: BannerCreate,
    _:   Admin        = Depends(require_permission("banners")),
    db:  AsyncSession = Depends(get_db),
):
    return await content_service.create_banner(db, req.model_dump())


@router.put("/banners/{banner_id}")
async def admin_update_banner(
    banner_id: int,
    req:       BannerUpdate,
    _:         Admin        = Depends(require_permission("banners")),
    db:        AsyncSession = Depends(get_db),
):
    return await content_service.update_banner(db, banner_id, req.model_dump(exclude_none=True))


@router.delete("/banners/{banner_id}", status_code=204)
async def admin_delete_banner(
    banner_id: int,
    _:         Admin        = Depends(require_permission("banners")),
    db:        AsyncSession = Depends(get_db),
):
    await content_service.delete_banner(db, banner_id)


# ── Coupons ───────────────────────────────────────────────────────────────────
@router.get("/coupons")
async def admin_list_coupons(
    _:  Admin        = Depends(require_permission("coupons")),
    db: AsyncSession = Depends(get_db),
):
    from app.models.marketing import Coupon
    r = await db.execute(select(Coupon).order_by(Coupon.created_at.desc()))
    return r.scalars().all()


class CouponCreate(BaseModel):
    code:             str
    type:             str
    value:            float         = 0
    min_order_amount: Optional[float]  = None
    max_uses:         Optional[int]    = None
    starts_at:        Optional[datetime] = None
    ends_at:          Optional[datetime] = None
    is_active:        bool           = True
    description:      Optional[str]  = None


class CouponUpdate(BaseModel):
    value:            Optional[float]    = None
    min_order_amount: Optional[float]    = None
    max_uses:         Optional[int]      = None
    starts_at:        Optional[datetime] = None
    ends_at:          Optional[datetime] = None
    is_active:        Optional[bool]     = None
    description:      Optional[str]      = None


@router.post("/coupons", status_code=201)
async def admin_create_coupon(
    req: CouponCreate,
    _:   Admin        = Depends(require_permission("coupons")),
    db:  AsyncSession = Depends(get_db),
):
    from app.models.marketing import Coupon
    data = req.model_dump()
    data["code"] = data["code"].upper().strip()
    r = await db.execute(select(Coupon).where(Coupon.code == data["code"]))
    if r.scalar_one_or_none():
        raise HTTPException(409, "Coupon code already exists")
    coupon = Coupon(**data)
    db.add(coupon)
    await db.flush()
    return coupon


@router.put("/coupons/{coupon_id}")
async def admin_update_coupon(
    coupon_id: int,
    req:       CouponUpdate,
    _:         Admin        = Depends(require_permission("coupons")),
    db:        AsyncSession = Depends(get_db),
):
    from app.models.marketing import Coupon
    r      = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = r.scalar_one_or_none()
    if not coupon:
        raise HTTPException(404, "Coupon not found")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(coupon, k, v)
    return coupon


@router.delete("/coupons/{coupon_id}", status_code=204)
async def admin_delete_coupon(
    coupon_id: int,
    _:         Admin        = Depends(require_permission("coupons")),
    db:        AsyncSession = Depends(get_db),
):
    from app.models.marketing import Coupon
    r      = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = r.scalar_one_or_none()
    if not coupon:
        raise HTTPException(404, "Coupon not found")
    await db.delete(coupon)


# ── Channels ──────────────────────────────────────────────────────────────────
@router.get("/channels")
async def admin_list_channels(
    _:  Admin        = Depends(require_permission("channels")),
    db: AsyncSession = Depends(get_db),
):
    return await content_service.list_channels(db)


class ChannelCreate(BaseModel):
    name:      str
    ref_code:  str
    platform:  Optional[str] = None
    is_active: bool          = True


class ChannelUpdate(BaseModel):
    name:      Optional[str]  = None
    platform:  Optional[str]  = None
    is_active: Optional[bool] = None


@router.post("/channels", status_code=201)
async def admin_create_channel(
    req: ChannelCreate,
    _:   Admin        = Depends(require_permission("channels")),
    db:  AsyncSession = Depends(get_db),
):
    return await content_service.create_channel(db, req.model_dump())


@router.put("/channels/{channel_id}")
async def admin_update_channel(
    channel_id: int,
    req:        ChannelUpdate,
    _:          Admin        = Depends(require_permission("channels")),
    db:         AsyncSession = Depends(get_db),
):
    return await content_service.update_channel(db, channel_id, req.model_dump(exclude_none=True))


@router.get("/channels/{channel_id}/stats")
async def admin_channel_stats(
    channel_id: int,
    _:          Admin        = Depends(require_permission("channels")),
    db:         AsyncSession = Depends(get_db),
):
    return await content_service.channel_stats(db, channel_id)


# ── Dashboard ─────────────────────────────────────────────────────────────────
@router.get("/dashboard")
async def admin_dashboard(
    _:  Admin        = Depends(require_permission("statistics")),
    db: AsyncSession = Depends(get_db),
):
    from app.models.order import Order
    from app.models.user import User
    from app.models.product import ProductReview, ProductSku
    from sqlalchemy import and_, cast, Date
    from datetime import date, timedelta

    now   = datetime.now(timezone.utc)
    today = now.date()
    month_start = today.replace(day=1)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)

    def paid_filter():
        return Order.payment_status == "paid"

    async def gmv(start=None, end=None):
        q = select(func.sum(Order.total_amount)).where(paid_filter())
        if start:
            q = q.where(Order.created_at >= start)
        if end:
            q = q.where(Order.created_at < end)
        r = await db.execute(q)
        return float(r.scalar_one() or 0)

    async def order_count(start=None, status_f=None):
        q = select(func.count(Order.id))
        if start:
            q = q.where(Order.created_at >= start)
        if status_f:
            q = q.where(Order.status == status_f)
        r = await db.execute(q)
        return r.scalar_one() or 0

    # GMV
    gmv_today       = await gmv(today, None)
    gmv_this_month  = await gmv(month_start, None)
    gmv_last_month  = await gmv(last_month_start, month_start)
    gmv_total       = await gmv()

    # Orders
    orders_today          = await order_count(today)
    orders_this_month     = await order_count(month_start)
    pending_shipment_cnt  = await order_count(status_f="pending_shipment")
    pending_payment_cnt   = await order_count(status_f="pending_payment")

    # Users
    r = await db.execute(select(func.count(User.id)).where(User.is_guest == False))
    total_users = r.scalar_one() or 0
    r = await db.execute(
        select(func.count(User.id))
        .where(User.is_guest == False, User.created_at >= today)
    )
    new_users_today = r.scalar_one() or 0
    r = await db.execute(
        select(func.count(User.id))
        .where(User.is_guest == False, User.created_at >= month_start)
    )
    new_users_month = r.scalar_one() or 0

    # Pending reviews
    r = await db.execute(
        select(func.count(ProductReview.id)).where(ProductReview.status == "pending")
    )
    pending_reviews = r.scalar_one() or 0

    # Top 10 products (30d)
    from app.models.order import OrderItem
    from app.models.product import Product
    thirty_days_ago = now.date() - timedelta(days=30)
    r = await db.execute(
        select(
            ProductSku.product_id,
            Product.name,
            func.sum(OrderItem.quantity).label("units_sold"),
            func.sum(OrderItem.subtotal).label("revenue"),
        )
        .join(OrderItem, OrderItem.sku_id == ProductSku.id)
        .join(Order,     Order.id         == OrderItem.order_id)
        .join(Product,   Product.id       == ProductSku.product_id)
        .where(Order.payment_status == "paid", Order.created_at >= thirty_days_ago)
        .group_by(ProductSku.product_id, Product.name)
        .order_by(func.sum(OrderItem.subtotal).desc())
        .limit(10)
    )
    top_products = [
        {
            "product_id":   row.product_id,
            "product_name": row.name,
            "units_sold":   int(row.units_sold or 0),
            "revenue":      float(row.revenue or 0),
        }
        for row in r.all()
    ]

    # Revenue by day (last 30 days)
    r = await db.execute(
        select(
            func.date(Order.created_at).label("date"),
            func.sum(Order.total_amount).label("revenue"),
        )
        .where(Order.payment_status == "paid", Order.created_at >= thirty_days_ago)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
    )
    rev_by_day_raw = {str(row.date): float(row.revenue or 0) for row in r.all()}
    # Zero-fill all 30 days
    rev_by_day = []
    for i in range(30):
        d = str(thirty_days_ago + timedelta(days=i))
        rev_by_day.append({"date": d, "revenue": rev_by_day_raw.get(d, 0.0)})

    # Recent 10 orders
    r = await db.execute(
        select(Order).order_by(Order.created_at.desc()).limit(10)
    )
    recent_orders = [
        {
            "id":           o.id,
            "order_no":     o.order_no,
            "status":       o.status,
            "total_amount": float(o.total_amount),
            "created_at":   o.created_at,
        }
        for o in r.scalars().all()
    ]

    return {
        "stats": {
            "gmv_today":               gmv_today,
            "gmv_this_month":          gmv_this_month,
            "gmv_last_month":          gmv_last_month,
            "gmv_total":               gmv_total,
            "orders_today":            orders_today,
            "orders_this_month":       orders_this_month,
            "orders_pending_shipment": pending_shipment_cnt,
            "orders_pending_payment":  pending_payment_cnt,
            "new_users_today":         new_users_today,
            "new_users_this_month":    new_users_month,
            "total_users":             total_users,
            "pending_reviews":         pending_reviews,
        },
        "top_products":  top_products,
        "recent_orders": recent_orders,
        "revenue_by_day":rev_by_day,
    }
