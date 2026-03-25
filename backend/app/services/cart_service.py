"""
Cart Service
============
Dual-track cart:
  - Logged-in users  → key: cart:user:{user_id}   TTL: 30 days
  - Guest users      → key: cart:guest:{token}     TTL: 7 days

Cart is stored as JSON in Redis:
  {sku_id: quantity, ...}

On checkout, cart is transferred to Order and cleared.
"""
from __future__ import annotations
import json
import secrets
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.redis import get_redis, RedisKeys
from app.core.storage import resolve_url
from app.models.product import ProductSku, Product, ProductImage
from app.schemas.cart import CartItemIn, CartOut, CartItemOut

USER_CART_TTL  = 60 * 60 * 24 * 30   # 30 days
GUEST_CART_TTL = 60 * 60 * 24 * 7    # 7 days


def _cart_key(user_id: Optional[int], guest_token: Optional[str]) -> tuple[str, int]:
    if user_id:
        return RedisKeys.cart_user(user_id), USER_CART_TTL
    if guest_token:
        return RedisKeys.cart_guest(guest_token), GUEST_CART_TTL
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication or guest token required")


async def _load_raw(key: str) -> dict[str, int]:
    redis = await get_redis()
    raw   = await redis.get(key)
    return json.loads(raw) if raw else {}


async def _save_raw(key: str, data: dict[str, int], ttl: int) -> None:
    redis = await get_redis()
    if data:
        await redis.setex(key, ttl, json.dumps(data))
    else:
        await redis.delete(key)


async def _hydrate(db: AsyncSession, raw: dict[str, int]) -> list[CartItemOut]:
    """Load SKU + product data from DB and build CartItemOut list."""
    if not raw:
        return []

    sku_ids = [int(k) for k in raw.keys()]
    q = (
        select(ProductSku)
        .where(ProductSku.id.in_(sku_ids), ProductSku.is_active == True)
        .options(
            selectinload(ProductSku.product)
            .selectinload(Product.images)
        )
    )
    skus = (await db.execute(q)).scalars().all()
    sku_map = {s.id: s for s in skus}

    items = []
    for sku_id_str, qty in raw.items():
        sku_id = int(sku_id_str)
        sku    = sku_map.get(sku_id)
        if not sku or not sku.product or not sku.product.is_published:
            continue   # skip stale/deleted SKUs

        cover = None
        if sku.product.images:
            img   = sku.product.images[0]
            cover = resolve_url(img.url, img.storage_type)

        items.append(CartItemOut(
            sku_id        = sku.id,
            sku_code      = sku.sku_code,
            product_id    = sku.product.id,
            product_name  = sku.product.name,
            product_slug  = sku.product.slug,
            variant_attrs = sku.variant_attrs,
            quantity      = qty,
            unit_price    = float(sku.price),
            compare_price = float(sku.compare_price) if sku.compare_price else None,
            subtotal      = round(float(sku.price) * qty, 2),
            stock         = sku.stock,
            cover_image   = cover,
            free_shipping = sku.free_shipping,
        ))
    return items


# ── Public API ────────────────────────────────────────────────────────────────
async def get_cart(
    db:          AsyncSession,
    user_id:     Optional[int]  = None,
    guest_token: Optional[str]  = None,
) -> CartOut:
    key, _ = _cart_key(user_id, guest_token)
    raw    = await _load_raw(key)
    items  = await _hydrate(db, raw)
    return CartOut(
        items      = items,
        item_count = sum(i.quantity for i in items),
        subtotal   = round(sum(i.subtotal for i in items), 2),
        guest_token= guest_token,
    )


async def add_to_cart(
    db:          AsyncSession,
    req:         CartItemIn,
    user_id:     Optional[int] = None,
    guest_token: Optional[str] = None,
) -> CartOut:
    # Validate SKU exists and has stock
    r   = await db.execute(
        select(ProductSku).where(ProductSku.id == req.sku_id, ProductSku.is_active == True)
    )
    sku = r.scalar_one_or_none()
    if not sku:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "SKU not found or unavailable")
    if sku.stock < req.quantity:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Only {sku.stock} units available",
        )

    key, ttl = _cart_key(user_id, guest_token)
    raw      = await _load_raw(key)
    current  = raw.get(str(req.sku_id), 0)
    new_qty  = current + req.quantity

    if new_qty > sku.stock:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Cannot add {req.quantity} more — only {sku.stock - current} units left",
        )

    raw[str(req.sku_id)] = new_qty
    await _save_raw(key, raw, ttl)
    return await get_cart(db, user_id, guest_token)


async def update_cart_item(
    db:          AsyncSession,
    sku_id:      int,
    quantity:    int,
    user_id:     Optional[int] = None,
    guest_token: Optional[str] = None,
) -> CartOut:
    key, ttl = _cart_key(user_id, guest_token)
    raw      = await _load_raw(key)

    if quantity <= 0:
        raw.pop(str(sku_id), None)
    else:
        r   = await db.execute(select(ProductSku).where(ProductSku.id == sku_id))
        sku = r.scalar_one_or_none()
        if not sku:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "SKU not found")
        if quantity > sku.stock:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Only {sku.stock} units available",
            )
        raw[str(sku_id)] = quantity

    await _save_raw(key, raw, ttl)
    return await get_cart(db, user_id, guest_token)


async def remove_from_cart(
    db:          AsyncSession,
    sku_id:      int,
    user_id:     Optional[int] = None,
    guest_token: Optional[str] = None,
) -> CartOut:
    return await update_cart_item(db, sku_id, 0, user_id, guest_token)


async def clear_cart(
    user_id:     Optional[int] = None,
    guest_token: Optional[str] = None,
) -> None:
    key, ttl = _cart_key(user_id, guest_token)
    await _save_raw(key, {}, ttl)


async def get_raw_cart(
    user_id:     Optional[int] = None,
    guest_token: Optional[str] = None,
) -> dict[str, int]:
    """Return raw {sku_id: qty} dict — used by checkout service."""
    key, _ = _cart_key(user_id, guest_token)
    return await _load_raw(key)


async def merge_guest_cart(
    db:          AsyncSession,
    user_id:     int,
    guest_token: str,
) -> None:
    """After guest logs in / registers — merge guest cart into user cart."""
    guest_key, _     = _cart_key(None, guest_token)
    user_key, u_ttl  = _cart_key(user_id, None)

    guest_raw = await _load_raw(guest_key)
    if not guest_raw:
        return

    user_raw = await _load_raw(user_key)
    for sku_id_str, qty in guest_raw.items():
        user_raw[sku_id_str] = user_raw.get(sku_id_str, 0) + qty

    await _save_raw(user_key, user_raw, u_ttl)
    redis = await get_redis()
    await redis.delete(guest_key)


def generate_guest_token() -> str:
    return secrets.token_urlsafe(32)
