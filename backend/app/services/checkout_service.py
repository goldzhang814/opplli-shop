"""
Checkout Service
================
Handles the full checkout flow:
  1. Preview (read-only): calculate totals, shipping, tax, coupon
  2. Place order: atomic 11-step flow
     - validate cart
     - validate coupon
     - calc shipping + tax
     - lock SKUs (SELECT FOR UPDATE)
     - check stock
     - deduct stock + write inventory_logs
     - create Order + OrderItems
     - save address to user if requested
     - clear cart
     - return payment intent data
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import ProductSku, Product
from app.models.order import Order, OrderItem, OrderStatusLog
from app.models.user import User, UserAddress
from app.models.marketing import MarketingChannel
from app.schemas.cart import (
    CheckoutPreviewRequest, CheckoutPreviewResponse,
    PlaceOrderRequest, PlaceOrderResponse,
    ShippingEstimateResponse, TaxEstimateResponse,
)
from app.services import cart_service, shipping_service, coupon_service
from app.models.shipping import ShippingRule
from app.core.storage import resolve_url


def _order_no() -> str:
    ts  = datetime.now(timezone.utc).strftime("%Y%m%d")
    uid = uuid.uuid4().hex[:8].upper()
    return f"ORD-{ts}-{uid}"


async def _resolve_channel(db: AsyncSession, ref: Optional[str]) -> Optional[int]:
    if not ref:
        return None
    r = await db.execute(
        select(MarketingChannel).where(
            MarketingChannel.ref_code  == ref,
            MarketingChannel.is_active == True,
        )
    )
    ch = r.scalar_one_or_none()
    return ch.id if ch else None


async def preview_checkout(
    db:          AsyncSession,
    req:         CheckoutPreviewRequest,
    user_id:     Optional[int],
    guest_token: Optional[str],
) -> CheckoutPreviewResponse:
    """Read-only price preview — does not create any records."""
    raw = await cart_service.get_raw_cart(user_id, guest_token)
    if not raw:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cart is empty")

    # Load SKUs
    sku_ids = [int(k) for k in raw.keys()]
    r       = await db.execute(
        select(ProductSku).where(ProductSku.id.in_(sku_ids))
    )
    skus    = {s.id: s for s in r.scalars().all()}

    subtotal = sum(float(skus[int(k)].price) * qty
                   for k, qty in raw.items() if int(k) in skus)
    subtotal = round(subtotal, 2)

    # Shipping
    shipping = await shipping_service.get_shipping_estimate(
        db, req.address.country_code, req.address.state_code, subtotal
    )
    if not shipping.deliverable:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            shipping.message or "Region not deliverable")

    shipping_fee = shipping.shipping_fee

    # Coupon
    coupon_resp  = None
    discount     = 0.0
    if req.coupon_code:
        coupon_resp = await coupon_service.validate_coupon(db, req.coupon_code, subtotal)
        if coupon_resp.valid:
            discount = coupon_resp.discount_amount or 0.0
            if coupon_resp.type == "free_shipping":
                shipping_fee = 0.0

    # Tax
    tax_resp = await shipping_service.get_tax_estimate(
        db, req.address.country_code, req.address.state_code,
        subtotal - discount, shipping_fee
    )

    total = round(subtotal - discount + shipping_fee + tax_resp.tax_amount, 2)

    return CheckoutPreviewResponse(
        subtotal                 = subtotal,
        shipping_fee             = shipping_fee,
        tax_amount               = tax_resp.tax_amount,
        discount_amount          = discount,
        total_amount             = max(0.0, total),
        coupon                   = coupon_resp,
        shipping                 = shipping,
        tax                      = tax_resp,
        free_shipping_threshold  = shipping.free_shipping_threshold,
        remaining_for_free       = shipping.remaining_for_free,
    )


async def place_order(
    db:          AsyncSession,
    req:         PlaceOrderRequest,
    user_id:     Optional[int],
    guest_email: Optional[str],
    guest_token: Optional[str],
) -> PlaceOrderResponse:
    """
    Atomic 11-step order creation flow.
    All DB writes happen in the same transaction.
    """
    # ── Step 1: Load + validate cart ─────────────────────────────────────────
    raw = await cart_service.get_raw_cart(user_id, guest_token)
    if not raw:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cart is empty")

    # ── Step 2: Validate coupon (reserve, don't redeem yet) ──────────────────
    coupon_id       = None
    discount_amount = 0.0
    free_ship_coupon= False
    if req.coupon_code:
        coupon_val = await coupon_service.validate_coupon(db, req.coupon_code, 0)  # subtotal TBD
        if not coupon_val.valid:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                f"Coupon error: {coupon_val.message}")

    # ── Step 3: Load SKUs with SELECT FOR UPDATE (lock rows) ─────────────────
    sku_ids = [int(k) for k in raw.keys()]
    r       = await db.execute(
        select(ProductSku)
        .where(ProductSku.id.in_(sku_ids))
        .with_for_update()
        .options(selectinload(ProductSku.product).selectinload(Product.images))
    )
    skus = {s.id: s for s in r.scalars().all()}

    # ── Step 4: Check stock ───────────────────────────────────────────────────
    for sku_id_str, qty in raw.items():
        sku_id = int(sku_id_str)
        sku    = skus.get(sku_id)
        if not sku or not sku.is_active:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                f"SKU {sku_id} is no longer available")
        if sku.stock < qty:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"'{sku.product.name}' only has {sku.stock} unit(s) left",
            )

    # ── Step 5: Calculate totals ──────────────────────────────────────────────
    subtotal = round(sum(float(skus[int(k)].price) * qty for k, qty in raw.items()), 2)

    # Re-validate coupon with real subtotal
    if req.coupon_code:
        discount_amount, coupon_id = await coupon_service.redeem_coupon(
            db, req.coupon_code, subtotal
        )
        if coupon_id is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Coupon no longer valid")
        coupon_val = await coupon_service.validate_coupon(db, req.coupon_code, subtotal)
        free_ship_coupon = (coupon_val.type == "free_shipping")

    shipping = await shipping_service.get_shipping_estimate(
        db, req.address.country_code, req.address.state_code, subtotal
    )
    if not shipping.deliverable:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            shipping.message or "Region not deliverable")

    shipping_fee = 0.0 if free_ship_coupon else shipping.shipping_fee

    # Shipping rule for snapshot
    rule = await shipping_service.get_shipping_rule_for_country(db, req.address.country_code)

    tax_resp = await shipping_service.get_tax_estimate(
        db, req.address.country_code, req.address.state_code,
        subtotal - discount_amount, shipping_fee
    )

    total = round(
        max(0.0, subtotal - discount_amount + shipping_fee + tax_resp.tax_amount), 2
    )

    # ── Step 6: Deduct stock + write inventory logs ───────────────────────────
    from app.models.product import InventoryLog
    for sku_id_str, qty in raw.items():
        sku    = skus[int(sku_id_str)]
        before = sku.stock
        sku.stock -= qty
        db.add(InventoryLog(
            sku_id      = sku.id,
            change_qty  = -qty,
            before_qty  = before,
            after_qty   = sku.stock,
            reason      = "order",
            reference_id= None,  # will update after order created
        ))

    # ── Step 7: Resolve channel ───────────────────────────────────────────────
    channel_id = await _resolve_channel(db, req.channel_ref)

    # ── Step 8: Create Order ──────────────────────────────────────────────────
    address_snapshot = req.address.model_dump()
    order = Order(
        order_no             = _order_no(),
        user_id              = user_id,
        status               = "pending_payment",
        subtotal             = subtotal,
        shipping_fee         = shipping_fee,
        tax_amount           = tax_resp.tax_amount,
        discount_amount      = discount_amount,
        total_amount         = total,
        payment_method       = req.payment_method,
        payment_status       = "unpaid",
        coupon_code          = req.coupon_code,
        shipping_address     = address_snapshot,
        shipping_zone_name   = shipping.zone_name,
        shipping_rule_id     = rule.id if rule else None,
        tax_rate_snapshot    = tax_resp.tax_rate if tax_resp else None,
        channel_ref          = req.channel_ref,
        channel_id           = channel_id,
        guest_email          = guest_email,
        language_code        = req.language_code,
        customer_note        = req.customer_note,
    )
    db.add(order)
    await db.flush()

    # ── Step 9: Create OrderItems ─────────────────────────────────────────────
    for sku_id_str, qty in raw.items():
        sku    = skus[int(sku_id_str)]
        cover  = None
        if sku.product and sku.product.images:
            img   = sku.product.images[0]
            cover = resolve_url(img.url, img.storage_type)
        db.add(OrderItem(
            order_id      = order.id,
            sku_id        = sku.id,
            product_name  = sku.product.name,
            sku_code      = sku.sku_code,
            variant_attrs = sku.variant_attrs,
            quantity      = qty,
            unit_price    = float(sku.price),
            subtotal      = round(float(sku.price) * qty, 2),
            product_image = cover,
        ))

    # Update inventory log reference_id with order.id
    from sqlalchemy import update as sa_update
    await db.execute(
        sa_update(InventoryLog)
        .where(InventoryLog.reference_id == None, InventoryLog.reason == "order")
        .values(reference_id=str(order.id))
    )

    # Status log
    db.add(OrderStatusLog(order_id=order.id, to_status="pending_payment"))

    # ── Step 10: Save address if requested ───────────────────────────────────
    if req.save_address and user_id:
        db.add(UserAddress(
            user_id       = user_id,
            full_name     = req.address.full_name,
            phone         = req.address.phone,
            country_code  = req.address.country_code,
            state_code    = req.address.state_code,
            state_name    = req.address.state_name,
            city          = req.address.city,
            address_line1 = req.address.address_line1,
            address_line2 = req.address.address_line2,
            postal_code   = req.address.postal_code,
        ))

    # ── Step 11: Clear cart ───────────────────────────────────────────────────
    await cart_service.clear_cart(user_id, guest_token)

    # Queue order confirmation email
    from app.tasks.email_tasks import send_order_confirmation
    email_to = guest_email or (
        (await db.execute(select(User).where(User.id == user_id))).scalar_one().email
        if user_id else None
    )
    if email_to:
        send_order_confirmation.delay(
            order_id      = order.id,
            email         = email_to,
            customer_name = req.address.full_name,
            language      = req.language_code,
        )

    return PlaceOrderResponse(
        order_id       = order.id,
        order_no       = order.order_no,
        total_amount   = total,
        payment_method = req.payment_method,
    )
