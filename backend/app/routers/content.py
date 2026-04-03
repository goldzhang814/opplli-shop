"""
Public Content Router
=====================
GET  /api/v1/blog                         — post list
GET  /api/v1/blog/{slug}                  — post detail
GET  /api/v1/blog/categories
GET  /api/v1/faq                          — FAQ list (by lang)
GET  /api/v1/faq/categories
GET  /api/v1/pages/{page_type}            — CMS page
GET  /api/v1/banners                      — active banners
POST /api/v1/newsletter/subscribe
GET  /api/v1/newsletter/unsubscribe
GET  /api/v1/sitemap.xml
GET  /api/v1/robots.txt
GET  /api/v1/i18n/{lang}                  — language pack
GET  /api/v1/cookie-consent               — cookie config
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.services import content_service
from app.config import settings

from app.models.marketing import MarketingChannel, ChannelEvent
import base64

router = APIRouter(tags=["Content"])


# ── Blog ──────────────────────────────────────────────────────────────────────
@router.get("/blog/categories")
async def blog_categories(db: AsyncSession = Depends(get_db)):
    return await content_service.list_blog_categories(db, active_only=True)


@router.get("/blog")
async def list_blog(
    page:        int           = Query(1, ge=1),
    limit:       int           = Query(10, ge=1, le=50),
    category_id: Optional[int] = None,
    db:          AsyncSession  = Depends(get_db),
):
    return await content_service.list_blog_posts(
        db, page=page, limit=limit,
        category_id=category_id, published_only=True,
    )


@router.get("/blog/{slug}")
async def get_blog_post(slug: str, db: AsyncSession = Depends(get_db)):
    return await content_service.get_blog_post_by_slug(db, slug, published_only=True)


# ── FAQ ───────────────────────────────────────────────────────────────────────
@router.get("/faq/categories")
async def faq_categories(
    lang: str          = Query("en", pattern="^(en|es)$"),
    db:   AsyncSession = Depends(get_db),
):
    return await content_service.faq_categories(db, lang)


@router.get("/faq")
async def list_faq(
    lang:     str           = Query("en", pattern="^(en|es)$"),
    category: Optional[str] = None,
    db:       AsyncSession  = Depends(get_db),
):
    return await content_service.list_faqs(db, lang=lang, category=category, active_only=True)


# ── CMS Pages ─────────────────────────────────────────────────────────────────
@router.get("/pages/{page_type}")
async def get_cms_page(
    page_type: str,
    lang:      str         = Query("en", pattern="^(en|es)$"),
    db:        AsyncSession = Depends(get_db),
):
    page = await content_service.get_cms_page(db, page_type, lang)
    if not page:
        from fastapi import HTTPException
        raise HTTPException(404, "Page not found")
    return {"page_type": page.page_type, "title": page.title, "content": page.content}


# ── Banners ───────────────────────────────────────────────────────────────────
@router.get("/banners")
async def active_banners(db: AsyncSession = Depends(get_db)):
    banners = await content_service.get_active_banners(db)
    return [
        {
            "id":       b.id,
            "title":    b.title,
            "subtitle": b.subtitle,
            "link_url": b.link_url,
            "coupon_id":b.coupon_id,
        }
        for b in banners
    ]


# ── Newsletter ────────────────────────────────────────────────────────────────
class SubscribeRequest(BaseModel):
    email:  EmailStr
    source: str = "footer"
    lang:   str = "en"


@router.post("/newsletter/subscribe", status_code=200)
async def newsletter_subscribe(
    req: SubscribeRequest,
    db:  AsyncSession = Depends(get_db),
):
    return await content_service.subscribe_newsletter(db, req.email, req.source, req.lang)


@router.get("/newsletter/unsubscribe")
async def newsletter_unsubscribe(
    token: str,
    db:    AsyncSession = Depends(get_db),
):
    result = await content_service.unsubscribe_newsletter(db, token)
    return result


# ── i18n ─────────────────────────────────────────────────────────────────────
@router.get("/i18n/{lang}")
async def get_language_pack(
    lang: str,
    db:   AsyncSession = Depends(get_db),
):
    if lang not in ("en", "es"):
        lang = "en"
    return await content_service.get_language_pack(db, lang)


@router.get("/settings/public")
async def public_settings(
    db: AsyncSession = Depends(get_db),
):
    keys = [
        "contact_email",
        "contact_whatsapp",
        "contact_facebook",
        "contact_telegram",
        "contact_phone",
        "company_name",
        "business_registration_number",
        "business_address",
    ]
    return await content_service.get_settings_by_keys(db, keys)


# ── Cookie consent ────────────────────────────────────────────────────────────
@router.get("/cookie-consent")
async def get_cookie_consent(
    lang: str          = Query("en", pattern="^(en|es)$"),
    db:   AsyncSession = Depends(get_db),
):
    cfg = await content_service.get_cookie_config(db, lang)
    if not cfg:
        return None
    return {
        "title":         cfg.title,
        "description":   cfg.description,
        "accept_btn":    cfg.accept_btn,
        "reject_btn":    cfg.reject_btn,
        "customize_btn": cfg.customize_btn,
    }


# ── Sitemap + robots ──────────────────────────────────────────────────────────
@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap(db: AsyncSession = Depends(get_db)):
    base_url = await content_service.get_setting(db, "site_url") or settings.FRONTEND_URL
    xml = await content_service.generate_sitemap(db, base_url.rstrip("/"))
    return Response(content=xml, media_type="application/xml")


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt(db: AsyncSession = Depends(get_db)):
    txt = await content_service.get_setting(db, "robots_txt")
    if not txt:
        txt = f"User-agent: *\nAllow: /\nSitemap: {settings.FRONTEND_URL}/sitemap.xml"
    return PlainTextResponse(txt)

@router.get("/track")
async def track_event(
    ref:        str,
    event:      str        = "visit",
    order_id:   int | None = None,
    db:         AsyncSession = Depends(get_db),
):
    # Find channel by ref_code
    r  = await db.execute(
        select(MarketingChannel).where(
            MarketingChannel.ref_code == ref,
            MarketingChannel.is_active == True,
        )
    )
    ch = r.scalar_one_or_none()
    if ch:
        db.add(ChannelEvent(
            channel_id = ch.id,
            event_type = event,
            order_id   = order_id,
        ))
        await db.commit()

    # Return 1x1 transparent GIF
    gif = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
    from fastapi.responses import Response
    return Response(content=gif, media_type="image/gif",
                    headers={"Cache-Control": "no-cache, no-store"})
