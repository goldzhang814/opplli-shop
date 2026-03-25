"""
Coupon Service
==============
Validates coupons and applies discounts.
Uses Redis lock to prevent concurrent over-redemption.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.marketing import Coupon
from app.core.redis import get_redis, RedisKeys
from app.schemas.cart import CouponValidateResponse

LOCK_TTL = 10  # seconds


async def validate_coupon(
    db:          AsyncSession,
    code:        str,
    order_total: float,
) -> CouponValidateResponse:
    """
    Validate a coupon code without redeeming it.
    Returns discount amount on success.
    """
    r      = await db.execute(select(Coupon).where(Coupon.code == code.upper().strip()))
    coupon = r.scalar_one_or_none()

    if not coupon:
        return CouponValidateResponse(valid=False, message="Coupon code not found")

    if not coupon.is_active:
        return CouponValidateResponse(valid=False, message="This coupon is no longer active")

    now = datetime.now(timezone.utc)
    if coupon.starts_at and coupon.starts_at.replace(tzinfo=timezone.utc) > now:
        return CouponValidateResponse(valid=False, message="This coupon is not yet valid")
    if coupon.ends_at and coupon.ends_at.replace(tzinfo=timezone.utc) < now:
        return CouponValidateResponse(valid=False, message="This coupon has expired")

    if coupon.max_uses is not None and coupon.used_count >= coupon.max_uses:
        return CouponValidateResponse(valid=False, message="This coupon has reached its usage limit")

    if coupon.min_order_amount and order_total < float(coupon.min_order_amount):
        return CouponValidateResponse(
            valid   = False,
            message = f"Minimum order amount is ${coupon.min_order_amount:.2f}",
        )

    discount = _calc_discount(coupon, order_total)
    return CouponValidateResponse(
        valid           = True,
        code            = coupon.code,
        type            = coupon.type,
        value           = float(coupon.value),
        discount_amount = discount,
    )


async def redeem_coupon(
    db:          AsyncSession,
    code:        str,
    order_total: float,
) -> tuple[float, Optional[int]]:
    """
    Atomically redeem a coupon.
    Returns (discount_amount, coupon_id).
    Uses Redis distributed lock to prevent race conditions.
    """
    redis    = await get_redis()
    lock_key = RedisKeys.coupon_lock(code)

    # Acquire lock
    acquired = await redis.set(lock_key, "1", ex=LOCK_TTL, nx=True)
    if not acquired:
        # Another request is redeeming — try validation without lock (safe read)
        result = await validate_coupon(db, code, order_total)
        if not result.valid:
            return 0.0, None
        return result.discount_amount or 0.0, None

    try:
        result = await validate_coupon(db, code, order_total)
        if not result.valid:
            return 0.0, None

        # Increment used_count
        r      = await db.execute(select(Coupon).where(Coupon.code == code.upper().strip()))
        coupon = r.scalar_one_or_none()
        if coupon:
            coupon.used_count += 1
            return result.discount_amount or 0.0, coupon.id

        return 0.0, None
    finally:
        await redis.delete(lock_key)


async def release_coupon(db: AsyncSession, code: str) -> None:
    """Decrement used_count if an order is cancelled before payment."""
    r      = await db.execute(select(Coupon).where(Coupon.code == code.upper().strip()))
    coupon = r.scalar_one_or_none()
    if coupon and coupon.used_count > 0:
        coupon.used_count -= 1


def _calc_discount(coupon: Coupon, order_total: float) -> float:
    if coupon.type == "percent":
        return round(order_total * float(coupon.value) / 100, 2)
    if coupon.type == "fixed":
        return min(float(coupon.value), order_total)
    if coupon.type == "free_shipping":
        return 0.0  # shipping discount applied separately
    return 0.0
