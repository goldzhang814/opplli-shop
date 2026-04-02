"""
Order Service
=============
Customer-facing order queries + admin order management.
"""
from __future__ import annotations
import math
from typing import Optional
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, OrderStatusLog
from app.models.shipping import Shipment, LogisticsCarrier
from app.models.payment import Payment
from app.schemas.order import ShipOrderRequest, AdminOrderUpdate


# ── Helpers ───────────────────────────────────────────────────────────────────
def _with_relations(q):
    return q.options(
        selectinload(Order.items).selectinload(OrderItem.sku),
        selectinload(Order.shipment).selectinload(Shipment.carrier),
        selectinload(Order.payments),
        selectinload(Order.status_logs),
    )

def _with_items(q):
    return q.options(
        selectinload(Order.items).selectinload(OrderItem.sku),
    )


def _build_order_out(order: Order) -> dict:
    shipment = None
    if order.shipment:
        s       = order.shipment
        carrier = s.carrier
        t_url   = None
        if carrier and carrier.tracking_url_template:
            t_url = carrier.tracking_url_template.replace("{tracking_no}", s.tracking_no)
        shipment = {
            "carrier_id":   s.carrier_id,
            "carrier_name": carrier.name if carrier else None,
            "tracking_no":  s.tracking_no,
            "tracking_url": t_url,
            "shipped_at":   s.shipped_at,
        }
    return {
        "id":                  order.id,
        "order_no":            order.order_no,
        "status":              order.status,
        "payment_method":      order.payment_method,
        "payment_status":      order.payment_status,
        "subtotal":            float(order.subtotal),
        "shipping_fee":        float(order.shipping_fee),
        "tax_amount":          float(order.tax_amount),
        "discount_amount":     float(order.discount_amount),
        "total_amount":        float(order.total_amount),
        "coupon_code":         order.coupon_code,
        "shipping_address":    order.shipping_address,
        "shipping_zone_name":  order.shipping_zone_name,
        "channel_ref":         order.channel_ref,
        "language_code":       order.language_code,
        "customer_note":       order.customer_note,
        "items":               [
            {
                "id":            i.id,
                "sku_id":        i.sku_id,
                "product_id":    i.sku.product_id if i.sku else None,
                "product_name":  i.product_name,
                "sku_code":      i.sku_code,
                "variant_attrs": i.variant_attrs,
                "quantity":      i.quantity,
                "unit_price":    float(i.unit_price),
                "subtotal":      float(i.subtotal),
                "product_image": i.product_image,
            }
            for i in order.items
        ],
        "shipment":  shipment,
        "created_at":order.created_at,
    }


# ── Customer ──────────────────────────────────────────────────────────────────
async def get_user_orders(
    db:      AsyncSession,
    user_id: int,
    page:    int = 1,
    limit:   int = 10,
) -> dict:
    q     = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(
        _with_items(q).offset((page - 1) * limit).limit(limit)
    )).scalars().all()

    return {
        "items": [
            {
                "id":             o.id,
                "order_no":       o.order_no,
                "status":         o.status,
                "payment_method": o.payment_method,
                "payment_status": o.payment_status,
                "total_amount":   float(o.total_amount),
                "item_count":     len(o.items),
                "created_at":     o.created_at,
                "items":          [
                    {
                        "id":            i.id,
                        "sku_id":        i.sku_id,
                        "product_id":    i.sku.product_id if i.sku else None,
                        "product_name":  i.product_name,
                        "sku_code":      i.sku_code,
                        "variant_attrs": i.variant_attrs,
                        "quantity":      i.quantity,
                        "unit_price":    float(i.unit_price),
                        "subtotal":      float(i.subtotal),
                        "product_image": i.product_image,
                    }
                    for i in o.items
                ],
            }
            for o in items
        ],
        "total": total,
        "page":  page,
        "pages": max(1, math.ceil(total / limit)),
    }


async def get_user_order_detail(
    db:       AsyncSession,
    order_id: int,
    user_id:  int,
) -> dict:
    q = _with_relations(
        select(Order).where(Order.id == order_id, Order.user_id == user_id)
    )
    r = await db.execute(q)
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    return _build_order_out(order)


async def cancel_order_by_user(
    db:       AsyncSession,
    order_id: int,
    user_id:  int,
) -> dict:
    r     = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user_id)
    )
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    if order.status != "pending_payment":
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Only pending_payment orders can be cancelled by the customer",
        )
    old_status   = order.status
    order.status = "cancelled"
    db.add(OrderStatusLog(
        order_id    = order_id,
        from_status = old_status,
        to_status   = "cancelled",
        note        = "Cancelled by customer",
    ))

    # Release coupon usage if applicable
    if order.coupon_code:
        from app.services.coupon_service import release_coupon
        await release_coupon(db, order.coupon_code)

    # Restore stock
    await _restore_stock(db, order_id)

    # Cancel email
    _queue_cancel_email(order)

    return {"id": order.id, "status": order.status}


async def request_refund_by_user(
    db:       AsyncSession,
    order_id: int,
    user_id:  int,
) -> dict:
    r     = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user_id)
    )
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    if order.status not in ("pending_shipment", "shipped", "completed"):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Order is not eligible for refund request",
        )
    old           = order.status
    order.status  = "refund_requested"
    db.add(OrderStatusLog(order_id=order_id, from_status=old, to_status="refund_requested",
                           note="Refund requested by customer"))
    return {"id": order.id, "status": order.status}


# ── Admin ─────────────────────────────────────────────────────────────────────
async def admin_list_orders(
    db:          AsyncSession,
    page:        int            = 1,
    limit:       int            = 20,
    status_f:    Optional[str]  = None,
    search:      Optional[str]  = None,
) -> dict:
    from sqlalchemy import or_
    from app.models.user import User
    q = select(Order).order_by(Order.created_at.desc())
    if status_f:
        q = q.where(Order.status == status_f)
    if search:
        like = f"%{search}%"
        q = q.join(User, User.id == Order.user_id, isouter=True).where(
            or_(
                Order.order_no.ilike(like),
                Order.guest_email.ilike(like),
                User.email.ilike(like),
            )
        )
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(
        _with_relations(q).offset((page - 1) * limit).limit(limit)
    )).scalars().all()

    return {
        "items": [
            {
                "id":             o.id,
                "order_no":       o.order_no,
                "status":         o.status,
                "payment_method": o.payment_method,
                "payment_status": o.payment_status,
                "total_amount":   float(o.total_amount),
                "item_count":     len(o.items),
                "user_id":        o.user_id,
                "guest_email":    o.guest_email,
                "channel_ref":    o.channel_ref,
                "created_at":     o.created_at,
            }
            for o in items
        ],
        "total": total,
        "page":  page,
        "pages": max(1, math.ceil(total / limit)),
    }


async def admin_get_order(db: AsyncSession, order_id: int) -> dict:
    q = _with_relations(select(Order).where(Order.id == order_id))
    r = await db.execute(q)
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    result = _build_order_out(order)
    result["user_id"]           = order.user_id
    result["guest_email"]       = order.guest_email
    result["admin_note"]        = order.admin_note
    result["tax_rate_snapshot"] = float(order.tax_rate_snapshot) if order.tax_rate_snapshot else None
    result["status_logs"]       = [
        {"from": l.from_status, "to": l.to_status, "note": l.note, "at": l.created_at}
        for l in order.status_logs
    ]
    return result


async def admin_update_order(
    db:       AsyncSession,
    order_id: int,
    req:      AdminOrderUpdate,
    admin_id: int,
) -> dict:
    r     = await db.execute(select(Order).where(Order.id == order_id))
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")

    if req.admin_note is not None:
        order.admin_note = req.admin_note

    if req.status and req.status != order.status:
        old_status   = order.status
        order.status = req.status
        db.add(OrderStatusLog(
            order_id    = order_id,
            from_status = old_status,
            to_status   = req.status,
            operator_id = admin_id,
        ))

        if req.status == "cancelled":
            await _restore_stock(db, order_id)
            if order.coupon_code:
                from app.services.coupon_service import release_coupon
                await release_coupon(db, order.coupon_code)
            _queue_cancel_email(order)

    return {"id": order.id, "status": order.status}


async def admin_ship_order(
    db:       AsyncSession,
    order_id: int,
    req:      ShipOrderRequest,
    admin_id: int,
) -> dict:
    r     = await db.execute(select(Order).where(Order.id == order_id))
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    if order.status != "pending_shipment":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Order is not in pending_shipment status")

    # Check carrier exists
    rc = await db.execute(
        select(LogisticsCarrier).where(LogisticsCarrier.id == req.carrier_id)
    )
    carrier = rc.scalar_one_or_none()
    if not carrier:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Carrier not found")

    shipment = Shipment(
        order_id    = order_id,
        carrier_id  = req.carrier_id,
        tracking_no = req.tracking_no,
        shipped_by  = admin_id,
        note        = req.note,
    )
    db.add(shipment)

    old_status   = order.status
    order.status = "shipped"
    db.add(OrderStatusLog(
        order_id    = order_id,
        from_status = old_status,
        to_status   = "shipped",
        operator_id = admin_id,
        note        = f"Shipped via {carrier.name}, tracking: {req.tracking_no}",
    ))

    # Build tracking URL
    tracking_url = None
    if carrier.tracking_url_template:
        tracking_url = carrier.tracking_url_template.replace("{tracking_no}", req.tracking_no)

    # Queue shipped email
    email = order.guest_email
    if not email and order.user_id:
        from app.models.user import User
        ru  = await db.execute(select(User).where(User.id == order.user_id))
        usr = ru.scalar_one_or_none()
        email = usr.email if usr else None

    if email:
        from app.tasks.email_tasks import send_order_shipped
        send_order_shipped.delay(
            order_id      = order_id,
            email         = email,
            customer_name = (order.shipping_address or {}).get("full_name", ""),
            carrier_name  = carrier.name,
            tracking_no   = req.tracking_no,
            tracking_url  = tracking_url or "",
            language      = order.language_code,
        )

    await db.flush()
    return {"id": order.id, "status": order.status, "tracking_no": req.tracking_no}


# ── Internal helpers ──────────────────────────────────────────────────────────
async def _restore_stock(db: AsyncSession, order_id: int) -> None:
    """Restore SKU stock when an order is cancelled."""
    from app.models.product import ProductSku, InventoryLog
    r = await db.execute(
        select(OrderItem).where(OrderItem.order_id == order_id)
    )
    items = r.scalars().all()
    for item in items:
        if not item.sku_id:
            continue
        rs  = await db.execute(select(ProductSku).where(ProductSku.id == item.sku_id))
        sku = rs.scalar_one_or_none()
        if sku:
            before    = sku.stock
            sku.stock += item.quantity
            db.add(InventoryLog(
                sku_id      = sku.id,
                change_qty  = item.quantity,
                before_qty  = before,
                after_qty   = sku.stock,
                reason      = "order_cancelled",
                reference_id= str(order_id),
            ))


def _queue_cancel_email(order: Order) -> None:
    from app.tasks.email_tasks import send_order_cancelled
    email = order.guest_email
    if not email and order.user_id:
        return  # email resolved async elsewhere
    if email:
        send_order_cancelled.delay(
            order_id      = order.id,
            email         = email,
            customer_name = (order.shipping_address or {}).get("full_name", ""),
            language      = order.language_code,
        )
