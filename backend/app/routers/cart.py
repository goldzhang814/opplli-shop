"""
Cart & Checkout Router
======================
GET    /api/v1/cart
POST   /api/v1/cart/items
PUT    /api/v1/cart/items/{sku_id}
DELETE /api/v1/cart/items/{sku_id}
DELETE /api/v1/cart
POST   /api/v1/cart/merge                  (merge guest → user after login)
POST   /api/v1/checkout/coupon/validate
POST   /api/v1/checkout/shipping-estimate
POST   /api/v1/checkout/preview
POST   /api/v1/checkout/place-order
GET    /api/v1/shipping-regions            (for address form country/state dropdown)
GET    /api/v1/track                       (channel tracking pixel)
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.core.dependencies import get_current_user_opt, get_current_user, get_guest_token
from app.models.user import User
from app.schemas.cart import (
    CartItemIn, CartOut,
    CouponValidateRequest, CouponValidateResponse,
    ShippingEstimateRequest, ShippingEstimateResponse,
    CheckoutPreviewRequest, CheckoutPreviewResponse,
    PlaceOrderRequest, PlaceOrderResponse,
)
from app.services import cart_service, shipping_service, coupon_service, checkout_service
from app.models.content import Country, CountryState
from app.models.shipping import ShippingRegion
from sqlalchemy import select

router = APIRouter(tags=["Cart & Checkout"])


def _ids(user: Optional[User], guest_token: Optional[str]) -> tuple[Optional[int], Optional[str]]:
    return (user.id if user else None), guest_token


# ── Cart ──────────────────────────────────────────────────────────────────────
@router.get("/cart", response_model=CartOut)
async def get_cart(
    user:        Optional[User] = Depends(get_current_user_opt),
    guest_token: Optional[str]  = Depends(get_guest_token),
    db:          AsyncSession   = Depends(get_db),
):
    user_id, gt = _ids(user, guest_token)
    if not user_id and not gt:
        return CartOut(items=[], item_count=0, subtotal=0.0)
    return await cart_service.get_cart(db, user_id, gt)


@router.post("/cart/items", response_model=CartOut, status_code=201)
async def add_to_cart(
    req:         CartItemIn,
    user:        Optional[User] = Depends(get_current_user_opt),
    guest_token: Optional[str]  = Depends(get_guest_token),
    db:          AsyncSession   = Depends(get_db),
):
    user_id, gt = _ids(user, guest_token)
    return await cart_service.add_to_cart(db, req, user_id, gt)


class UpdateQtyRequest(BaseModel):
    quantity: int


@router.put("/cart/items/{sku_id}", response_model=CartOut)
async def update_cart_item(
    sku_id:      int,
    req:         UpdateQtyRequest,
    user:        Optional[User] = Depends(get_current_user_opt),
    guest_token: Optional[str]  = Depends(get_guest_token),
    db:          AsyncSession   = Depends(get_db),
):
    user_id, gt = _ids(user, guest_token)
    return await cart_service.update_cart_item(db, sku_id, req.quantity, user_id, gt)


@router.delete("/cart/items/{sku_id}", response_model=CartOut)
async def remove_cart_item(
    sku_id:      int,
    user:        Optional[User] = Depends(get_current_user_opt),
    guest_token: Optional[str]  = Depends(get_guest_token),
    db:          AsyncSession   = Depends(get_db),
):
    user_id, gt = _ids(user, guest_token)
    return await cart_service.remove_from_cart(db, sku_id, user_id, gt)


@router.delete("/cart", status_code=204)
async def clear_cart(
    user:        Optional[User] = Depends(get_current_user_opt),
    guest_token: Optional[str]  = Depends(get_guest_token),
):
    user_id, gt = _ids(user, guest_token)
    await cart_service.clear_cart(user_id, gt)


class MergeCartRequest(BaseModel):
    guest_token: str


@router.post("/cart/merge", status_code=204)
async def merge_cart(
    req:  MergeCartRequest,
    user: User         = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    """Call this after user logs in while having a guest cart."""
    await cart_service.merge_guest_cart(db, user.id, req.guest_token)


# ── Checkout ──────────────────────────────────────────────────────────────────
@router.post("/checkout/coupon/validate", response_model=CouponValidateResponse)
async def validate_coupon(
    req: CouponValidateRequest,
    db:  AsyncSession = Depends(get_db),
):
    return await coupon_service.validate_coupon(db, req.code, req.order_total)


@router.post("/checkout/shipping-estimate", response_model=ShippingEstimateResponse)
async def shipping_estimate(
    req: ShippingEstimateRequest,
    db:  AsyncSession = Depends(get_db),
):
    return await shipping_service.get_shipping_estimate(
        db, req.country_code, req.state_code, req.subtotal
    )


@router.post("/checkout/preview", response_model=CheckoutPreviewResponse)
async def checkout_preview(
    req:         CheckoutPreviewRequest,
    user:        Optional[User] = Depends(get_current_user_opt),
    guest_token: Optional[str]  = Depends(get_guest_token),
    db:          AsyncSession   = Depends(get_db),
):
    user_id, gt = _ids(user, guest_token)
    return await checkout_service.preview_checkout(db, req, user_id, gt)


@router.post("/checkout/place-order", response_model=PlaceOrderResponse, status_code=201)
async def place_order(
    req:         PlaceOrderRequest,
    user:        Optional[User] = Depends(get_current_user_opt),
    guest_token: Optional[str]  = Depends(get_guest_token),
    db:          AsyncSession   = Depends(get_db),
):
    user_id    = user.id if user else None
    guest_email= None
    if not user_id:
        # Guest — email must exist on their JWT guest account
        if not guest_token:
            from fastapi import HTTPException
            raise HTTPException(401, "Authentication or guest token required")
        # Retrieve guest email
        from app.models.user import User as UserModel
        from sqlalchemy import select
        # guest email resolved from their account
        gt_user = None
        guest_email = req.address.full_name  # fallback — real impl resolves from DB

    result = await checkout_service.place_order(
        db, req, user_id, guest_email, guest_token
    )
    return result


# ── Shipping regions (for address form) ───────────────────────────────────────
@router.get("/shipping-regions/countries")
async def get_shippable_countries(db: AsyncSession = Depends(get_db)):
    """Return countries that have at least one enabled shipping region."""
    r = await db.execute(
        select(ShippingRegion.country_code)
        .where(ShippingRegion.enabled == True)
        .distinct()
    )
    codes = [row[0] for row in r.all()]

    r2 = await db.execute(
        select(Country).where(Country.code.in_(codes), Country.is_active == True)
        .order_by(Country.sort_order, Country.name)
    )
    countries = r2.scalars().all()
    return [{"code": c.code, "name": c.name} for c in countries]


@router.get("/shipping-regions/states/{country_code}")
async def get_shippable_states(country_code: str, db: AsyncSession = Depends(get_db)):
    """
    For US: return states where ShippingRegion.enabled = True.
    For other countries: return all states from country_states table.
    """
    if country_code.upper() == "US":
        r = await db.execute(
            select(ShippingRegion).where(
                ShippingRegion.country_code == "US",
                ShippingRegion.enabled      == True,
                ShippingRegion.state_code   != None,
            )
        )
        regions = r.scalars().all()
        codes   = [reg.state_code for reg in regions]
        r2 = await db.execute(
            select(CountryState)
            .where(CountryState.country_code == "US", CountryState.code.in_(codes))
            .order_by(CountryState.name)
        )
        states = r2.scalars().all()
    else:
        r2 = await db.execute(
            select(CountryState)
            .where(CountryState.country_code == country_code, CountryState.is_active == True)
            .order_by(CountryState.name)
        )
        states = r2.scalars().all()

    return [{"code": s.code, "name": s.name} for s in states]


# ── Channel tracking pixel ────────────────────────────────────────────────────
@router.get("/track")
async def track_channel(
    ref:        str,
    event:      str           = Query("visit", pattern="^(visit|add_to_cart|order)$"),
    session_id: Optional[str] = None,
    db:         AsyncSession  = Depends(get_db),
):
    """
    GET /track?ref=instagram&event=visit
    Records channel event. Returns 204 transparent pixel.
    """
    from app.models.marketing import MarketingChannel, ChannelEvent
    r  = await db.execute(
        select(MarketingChannel).where(
            MarketingChannel.ref_code  == ref,
            MarketingChannel.is_active == True,
        )
    )
    ch = r.scalar_one_or_none()
    if ch:
        db.add(ChannelEvent(channel_id=ch.id, event_type=event, session_id=session_id))

    # Return 1×1 transparent GIF
    gif = b"GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;"
    return Response(content=gif, media_type="image/gif", status_code=200)
