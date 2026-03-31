"""
Orders & Payments Router (customer-facing)
==========================================
GET  /api/v1/orders                       - my orders list
GET  /api/v1/orders/{id}                  - order detail
POST /api/v1/orders/{id}/cancel           - cancel (pending_payment only)
POST /api/v1/orders/{id}/refund-request   - request refund

Payment initiation (called right after place-order):
POST /api/v1/payments/stripe/intent       - create Stripe PaymentIntent
POST /api/v1/payments/paypal/order        - create PayPal order
GET  /api/v1/payments/paypal/capture      - capture PayPal after redirect
POST /api/v1/payments/airwallex/intent    - create Airwallex PaymentIntent

Webhooks (called by payment providers):
POST /api/v1/webhooks/stripe
POST /api/v1/webhooks/paypal
POST /api/v1/webhooks/airwallex
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.order import PaginatedOrders, OrderOut
from app.services import order_service, payment_service

router = APIRouter(tags=["Orders & Payments"])


# ── My Orders ─────────────────────────────────────────────────────────────────
@router.get("/orders", response_model=PaginatedOrders)
async def my_orders(
    page: int         = Query(1, ge=1),
    user: User        = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    return await order_service.get_user_orders(db, user.id, page=page)


@router.get("/orders/{order_id}")
async def my_order_detail(
    order_id: int,
    user:     User        = Depends(get_current_user),
    db:       AsyncSession = Depends(get_db),
):
    return await order_service.get_user_order_detail(db, order_id, user.id)


@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    user:     User        = Depends(get_current_user),
    db:       AsyncSession = Depends(get_db),
):
    return await order_service.cancel_order_by_user(db, order_id, user.id)


@router.post("/orders/{order_id}/refund-request")
async def request_refund(
    order_id: int,
    user:     User        = Depends(get_current_user),
    db:       AsyncSession = Depends(get_db),
):
    return await order_service.request_refund_by_user(db, order_id, user.id)


# ── Payment Initiation ────────────────────────────────────────────────────────
class PaymentIntentRequest(BaseModel):
    order_id: int


@router.post("/payments/stripe/intent")
async def stripe_payment_intent(
    req:  PaymentIntentRequest,
    user: User        = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    order = await order_service.get_user_order_detail(db, req.order_id, user.id)
    return await payment_service.stripe_create_payment_intent(
        db, req.order_id, order["total_amount"]
    )


@router.post("/payments/paypal/order")
async def paypal_create_order(
    req:  PaymentIntentRequest,
    user: User        = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    order = await order_service.get_user_order_detail(db, req.order_id, user.id)
    return await payment_service.paypal_create_order(
        db, req.order_id, order["total_amount"]
    )


@router.get("/payments/paypal/capture")
async def paypal_capture(
    token:    str,
    order_id: int,
    db:       AsyncSession = Depends(get_db),
):
    """Called when PayPal redirects back after buyer approval."""
    await payment_service.paypal_capture_order(db, token, order_id)
    return {"status": "captured", "order_id": order_id}


@router.post("/payments/airwallex/intent")
async def airwallex_payment_intent(
    req:  PaymentIntentRequest,
    user: User        = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    order = await order_service.get_user_order_detail(db, req.order_id, user.id)
    return await payment_service.airwallex_create_payment_intent(
        db, req.order_id, order["total_amount"]
    )


# ── Webhooks ──────────────────────────────────────────────────────────────────
@router.post("/webhooks/stripe", status_code=200)
async def stripe_webhook(
    request:       Request,
    stripe_signature: str = Header(alias="stripe-signature"),
    db:            AsyncSession = Depends(get_db),
):
    payload = await request.body()
    event   = payment_service.stripe_verify_webhook(payload, stripe_signature)
    await payment_service.handle_stripe_webhook(db, event)
    return {"received": True}


@router.post("/webhooks/paypal", status_code=200)
async def paypal_webhook(
    request: Request,
    db:      AsyncSession = Depends(get_db),
):
    payload = await request.body()
    headers = dict(request.headers)
    await payment_service.handle_paypal_webhook(db, payload, headers)
    return {"received": True}


@router.post("/webhooks/airwallex", status_code=200)
async def airwallex_webhook(
    request: Request,
    db:      AsyncSession = Depends(get_db),
):
    payload = await request.body()
    await payment_service.handle_airwallex_webhook(db, payload, request.headers)
    return {"received": True}
