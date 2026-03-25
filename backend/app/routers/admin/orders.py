"""
Admin Orders Router
====================
GET    /api/v1/admin/orders
GET    /api/v1/admin/orders/{id}
PUT    /api/v1/admin/orders/{id}
POST   /api/v1/admin/orders/{id}/ship
POST   /api/v1/admin/orders/{id}/refund
GET    /api/v1/admin/payment-webhooks
GET    /api/v1/admin/payment-webhooks/{id}
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.dependencies import require_permission
from app.models.admin import Admin
from app.models.payment import PaymentWebhook
from app.schemas.order import AdminOrderUpdate, ShipOrderRequest, RefundRequest
from app.services import order_service, payment_service

router = APIRouter(prefix="/admin", tags=["Admin — Orders"])


@router.get("/orders")
async def admin_list_orders(
    page:   int           = Query(1, ge=1),
    status: Optional[str] = None,
    search: Optional[str] = None,
    _:      Admin         = Depends(require_permission("orders")),
    db:     AsyncSession  = Depends(get_db),
):
    return await order_service.admin_list_orders(
        db, page=page, status_f=status, search=search
    )


@router.get("/orders/{order_id}")
async def admin_get_order(
    order_id: int,
    _:        Admin        = Depends(require_permission("orders")),
    db:       AsyncSession = Depends(get_db),
):
    return await order_service.admin_get_order(db, order_id)


@router.put("/orders/{order_id}")
async def admin_update_order(
    order_id: int,
    req:      AdminOrderUpdate,
    admin:    Admin        = Depends(require_permission("orders")),
    db:       AsyncSession = Depends(get_db),
):
    return await order_service.admin_update_order(db, order_id, req, admin.id)


@router.post("/orders/{order_id}/ship")
async def admin_ship_order(
    order_id: int,
    req:      ShipOrderRequest,
    admin:    Admin        = Depends(require_permission("orders")),
    db:       AsyncSession = Depends(get_db),
):
    return await order_service.admin_ship_order(db, order_id, req, admin.id)


@router.post("/orders/{order_id}/refund")
async def admin_refund_order(
    order_id: int,
    req:      RefundRequest,
    admin:    Admin        = Depends(require_permission("payments")),
    db:       AsyncSession = Depends(get_db),
):
    return await payment_service.process_refund(
        db, order_id, req.amount, req.reason, admin.id
    )


# ── Webhook logs ──────────────────────────────────────────────────────────────
@router.get("/payment-webhooks")
async def list_webhooks(
    page:     int           = Query(1, ge=1),
    provider: Optional[str] = None,
    _:        Admin         = Depends(require_permission("payments")),
    db:       AsyncSession  = Depends(get_db),
):
    from sqlalchemy import func
    import math
    q = select(PaymentWebhook).order_by(PaymentWebhook.created_at.desc())
    if provider:
        q = q.where(PaymentWebhook.provider == provider)
    total = (await db.execute(
        select(func.count()).select_from(q.subquery())
    )).scalar_one()
    limit = 20
    items = (await db.execute(q.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {
        "items": [
            {
                "id":           w.id,
                "provider":     w.provider,
                "event_type":   w.event_type,
                "event_id":     w.event_id,
                "order_id":     w.order_id,
                "status":       w.status,
                "created_at":   w.created_at,
                "processed_at": w.processed_at,
            }
            for w in items
        ],
        "total": total,
        "page":  page,
        "pages": max(1, math.ceil(total / limit)),
    }


@router.get("/payment-webhooks/{webhook_id}")
async def get_webhook_detail(
    webhook_id: int,
    _:          Admin        = Depends(require_permission("payments")),
    db:         AsyncSession = Depends(get_db),
):
    r = await db.execute(select(PaymentWebhook).where(PaymentWebhook.id == webhook_id))
    w = r.scalar_one_or_none()
    if not w:
        from fastapi import HTTPException, status
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Webhook not found")
    return {
        "id":           w.id,
        "provider":     w.provider,
        "event_type":   w.event_type,
        "event_id":     w.event_id,
        "order_id":     w.order_id,
        "status":       w.status,
        "raw_payload":  w.raw_payload,
        "error_msg":    w.error_msg,
        "created_at":   w.created_at,
        "processed_at": w.processed_at,
    }
