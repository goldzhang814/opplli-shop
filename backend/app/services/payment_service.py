"""
Payment Service
===============
Unified abstraction over Stripe, PayPal, and Airwallex.
Keys are NEVER stored in DB — always read from settings (env vars).

Flow per provider:
  Stripe:    create PaymentIntent → client_secret → frontend confirms → webhook
  PayPal:    create order → approval_url → redirect → capture on return
  Airwallex: create PaymentIntent → client_secret → frontend confirms → webhook

Refunds:
  All three providers support full + partial refunds via their respective APIs.
"""
from __future__ import annotations
import hashlib
import hmac
import json
import time
import uuid
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from typing import Optional

import httpx
import stripe
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.payment import Payment, Refund, PaymentWebhook
from app.models.order import Order, OrderStatusLog

import logging
logger = logging.getLogger("uvicorn.error")

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


# ── Stripe ────────────────────────────────────────────────────────────────────
async def stripe_create_payment_intent(
    db:       AsyncSession,
    order_id: int,
    amount:   float,
) -> dict:
    """
    Creates a Stripe PaymentIntent and records it in DB.
    Returns client_secret for frontend Stripe Elements.
    """
    amount_cents = int(round(amount * 100))
    try:
        intent = stripe.PaymentIntent.create(
            amount          = amount_cents,
            currency        = "usd",
            metadata        = {"order_id": str(order_id)},
            automatic_payment_methods = {"enabled": True},
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Stripe error: {e.user_message}")

    payment = Payment(
        order_id            = order_id,
        provider            = "stripe",
        provider_payment_id = intent["id"],
        amount              = amount,
        currency            = "USD",
        status              = "pending",
        raw_response        = dict(intent),
    )
    db.add(payment)
    await db.flush()

    return {
        "client_secret":     intent["client_secret"],
        "payment_intent_id": intent["id"],
    }


def stripe_verify_webhook(payload: bytes, sig_header: str) -> dict:
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return dict(event)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid Stripe webhook signature")


async def handle_stripe_webhook(db: AsyncSession, event: dict) -> None:
    event_type = event["type"]
    event_id   = event["id"]

    # Dedup
    r = await db.execute(
        select(PaymentWebhook).where(PaymentWebhook.event_id == event_id)
    )
    if r.scalar_one_or_none():
        return

    obj       = event["data"]["object"]
    order_id  = int(obj.get("metadata", {}).get("order_id", 0)) or None

    webhook = PaymentWebhook(
        provider    = "stripe",
        event_type  = event_type,
        event_id    = event_id,
        order_id    = order_id,
        status      = "processing",
        raw_payload = event,
    )
    db.add(webhook)
    await db.flush()

    try:
        if event_type == "payment_intent.succeeded":
            await _on_payment_success(db, "stripe", obj["id"], order_id, obj)
        elif event_type in ("payment_intent.payment_failed", "payment_intent.canceled"):
            await _on_payment_failed(db, "stripe", obj["id"], order_id, obj,
                                     obj.get("last_payment_error", {}).get("message", "Payment failed"))
        webhook.status      = "processed"
        webhook.processed_at= datetime.now(timezone.utc)
    except Exception as exc:
        webhook.status    = "error"
        webhook.error_msg = str(exc)
        raise


# ── PayPal ────────────────────────────────────────────────────────────────────
_paypal_token_cache: dict = {}


async def _paypal_access_token() -> str:
    """Get (cached) PayPal OAuth2 access token."""
    cached = _paypal_token_cache.get("token")
    if cached and _paypal_token_cache.get("expires_at", 0) > time.time() + 60:
        return cached

    base = (
        "https://api-m.paypal.com"
        if settings.PAYPAL_MODE == "live"
        else "https://api-m.sandbox.paypal.com"
    )
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{base}/v1/oauth2/token",
            auth    = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
            data    = {"grant_type": "client_credentials"},
            headers = {"Content-Type": "application/x-www-form-urlencoded"},
        )
        r.raise_for_status()
        data = r.json()

    _paypal_token_cache["token"]      = data["access_token"]
    _paypal_token_cache["expires_at"] = time.time() + data.get("expires_in", 3600)
    return data["access_token"]


def _paypal_base() -> str:
    return (
        "https://api-m.paypal.com"
        if settings.PAYPAL_MODE == "live"
        else "https://api-m.sandbox.paypal.com"
    )


async def paypal_create_order(
    db:       AsyncSession,
    order_id: int,
    amount:   float,
) -> dict:
    token   = await _paypal_access_token()
    base    = _paypal_base()
    return_url = f"{settings.FRONTEND_URL}/checkout/paypal/return?order_id={order_id}"
    cancel_url = f"{settings.FRONTEND_URL}/checkout/paypal/cancel?order_id={order_id}"

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{base}/v2/checkout/orders",
            json    = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount":      {"currency_code": "USD", "value": f"{amount:.2f}"},
                    "custom_id":   str(order_id),
                }],
                "application_context": {
                    "return_url": return_url,
                    "cancel_url": cancel_url,
                },
            },
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type":  "application/json",
            },
        )
        r.raise_for_status()
        data = r.json()

    approval_url = next(
        (link["href"] for link in data.get("links", []) if link["rel"] == "approve"),
        None,
    )
    if not approval_url:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "PayPal approval URL not found")

    payment = Payment(
        order_id            = order_id,
        provider            = "paypal",
        provider_payment_id = data["id"],
        amount              = amount,
        currency            = "USD",
        status              = "pending",
        raw_response        = data,
    )
    db.add(payment)
    await db.flush()

    return {"paypal_order_id": data["id"], "approval_url": approval_url}


async def paypal_capture_order(
    db:             AsyncSession,
    paypal_order_id:str,
    order_id:       int,
) -> None:
    token = await _paypal_access_token()
    base  = _paypal_base()

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{base}/v2/checkout/orders/{paypal_order_id}/capture",
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type":  "application/json",
            },
        )
        r.raise_for_status()
        data = r.json()

    capture_id = (
        data.get("purchase_units", [{}])[0]
            .get("payments", {})
            .get("captures", [{}])[0]
            .get("id")
    )
    cap_status = data.get("status", "").upper()

    if cap_status == "COMPLETED":
        await _on_payment_success(db, "paypal", capture_id or paypal_order_id, order_id, data)
    else:
        await _on_payment_failed(db, "paypal", paypal_order_id, order_id, data, "PayPal capture failed")


async def handle_paypal_webhook(db: AsyncSession, payload: bytes, headers: dict) -> None:
    """Verify PayPal webhook and route event."""
    # PayPal webhook verification (simplified — use PayPal SDK in production)
    try:
        event = json.loads(payload)
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid JSON payload")

    event_type = event.get("event_type", "")
    event_id   = event.get("id", "")

    r = await db.execute(
        select(PaymentWebhook).where(PaymentWebhook.event_id == event_id)
    )
    if r.scalar_one_or_none():
        return

    resource  = event.get("resource", {})
    custom_id = resource.get("custom_id") or resource.get("purchase_units", [{}])[0].get("custom_id")
    order_id  = int(custom_id) if custom_id and custom_id.isdigit() else None

    webhook = PaymentWebhook(
        provider    = "paypal",
        event_type  = event_type,
        event_id    = event_id,
        order_id    = order_id,
        status      = "processing",
        raw_payload = event,
    )
    db.add(webhook)
    await db.flush()

    try:
        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            await _on_payment_success(db, "paypal", resource.get("id", ""), order_id, resource)
        elif event_type in ("PAYMENT.CAPTURE.DENIED", "PAYMENT.CAPTURE.REVERSED"):
            await _on_payment_failed(db, "paypal", resource.get("id", ""), order_id, resource,
                                     "PayPal payment denied or reversed")
        webhook.status       = "processed"
        webhook.processed_at = datetime.now(timezone.utc)
    except Exception as exc:
        webhook.status    = "error"
        webhook.error_msg = str(exc)
        raise


# ── Airwallex ─────────────────────────────────────────────────────────────────
_awx_token_cache: dict = {}


async def _awx_access_token() -> str:
    cached = _awx_token_cache.get("token")
    if cached and _awx_token_cache.get("expires_at", 0) > time.time() + 60:
        return cached

    base = (
        "https://api.airwallex.com"
        if settings.AIRWALLEX_ENV == "prod"
        else "https://api-demo.airwallex.com"
    )
    async with httpx.AsyncClient() as client:
        # 先测出口 IP
        ip = await client.get("https://ifconfig.me/ip")
        logger.info("AWX request exit IP: %s", ip.text)

        r = await client.post(
            f"{base}/api/v1/authentication/login",
            headers = {
                "x-client-id": settings.AIRWALLEX_CLIENT_ID,
                "x-api-key":   settings.AIRWALLEX_API_KEY,
                "User-Agent":   "Mozilla/5.0",  # 加这行
                "Content-Type": "application/json",
            },
            content=b"",  # 加这行，确保 Content-Length: 0 被发送
        )
        logger.error("AWX response status=%s body=%s", r.status_code, r.text)
        if r.status_code >= 400:
            try:
                err = r.json()
            except Exception:
                err = {"message": r.text}
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Airwallex error: {err}",
            )

        r.raise_for_status()
        data = r.json()

    _awx_token_cache["token"]      = data["token"]
    _awx_token_cache["expires_at"] = time.time() + data.get("expires_in", 1800)
    return data["token"]


def _awx_base() -> str:
    return (
        "https://api.airwallex.com"
        if settings.AIRWALLEX_ENV == "prod"
        else "https://api-demo.airwallex.com"
    )


async def airwallex_create_payment_intent(
    db:       AsyncSession,
    order_id: int,
    amount:   float,
) -> dict:
    token = await _awx_access_token()
    base  = _awx_base()
    request_id = str(uuid.uuid4())
    amount_value = float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{base}/api/v1/pa/payment_intents/create",
            json    = {
                "request_id":       request_id,
                "amount":           amount_value,
                "currency":         "USD",
                "merchant_order_id":str(order_id),
                "order":            {"type": "physical_goods"},
            },
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type":  "application/json",
            },
        )
        if r.status_code >= 400:
            try:
                err = r.json()
            except Exception:
                err = {"message": r.text}
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Airwallex error: {err}",
            )
        data = r.json()

    payment = Payment(
        order_id            = order_id,
        provider            = "airwallex",
        provider_payment_id = data["id"],
        amount              = amount,
        currency            = "USD",
        status              = "pending",
        raw_response        = data,
    )
    db.add(payment)
    await db.flush()

    return {
        "payment_intent_id": data["id"],
        "client_secret":     data.get("client_secret", ""),
    }


def _awx_verify_signature(payload: bytes, signature: str, timestamp: str) -> bool:
    secret = (settings.AIRWALLEX_WEBHOOK_SECRET or "").strip()
    if not secret or not signature or not timestamp:
        return False
    message = timestamp.encode("utf-8") + payload
    expected = hmac.new(
        secret.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def _normalize_headers(headers: object) -> dict[str, str]:
    try:
        items = headers.items()
    except Exception:
        return {}
    return {str(k).lower(): str(v) for k, v in items}


async def handle_airwallex_webhook(db: AsyncSession, payload: bytes, headers: object) -> None:
    hdrs = _normalize_headers(headers)
    sig = hdrs.get("x-signature", "")
    ts  = hdrs.get("x-timestamp", "")

    logger.info(
        "airwallex webhook received headers=%s signature_present=%s payload_len=%s",
        list(hdrs.keys()), bool(sig), len(payload),
    )

    if settings.AIRWALLEX_WEBHOOK_SECRET and not _awx_verify_signature(payload, sig, ts):
        logger.warning("airwallex webhook signature invalid")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid Airwallex signature")

    try:
        event = json.loads(payload)
    except Exception:
        logger.exception("airwallex webhook invalid json")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid JSON")

    event_type = event.get("name", "")
    event_id   = event.get("id", event_type + str(time.time()))
    resource   = event.get("data", {}).get("object", {})
    order_id_s = resource.get("merchant_order_id")
    order_id   = int(order_id_s) if order_id_s and order_id_s.isdigit() else None

    r = await db.execute(
        select(PaymentWebhook).where(PaymentWebhook.event_id == event_id)
    )
    if r.scalar_one_or_none():
        return

    webhook = PaymentWebhook(
        provider    = "airwallex",
        event_type  = event_type,
        event_id    = event_id,
        order_id    = order_id,
        status      = "processing",
        raw_payload = event,
    )
    db.add(webhook)
    await db.flush()

    try:
        if event_type == "payment_intent.succeeded":
            await _on_payment_success(db, "airwallex", resource.get("id", ""), order_id, resource)
        elif event_type in ("payment_intent.cancelled", "payment_intent.failed"):
            await _on_payment_failed(
                db, "airwallex", resource.get("id", ""), order_id, resource,
                resource.get("cancellation_reason") or "Payment failed",
            )
        webhook.status       = "processed"
        webhook.processed_at = datetime.now(timezone.utc)
    except Exception as exc:
        webhook.status    = "error"
        webhook.error_msg = str(exc)
        raise


# ── Shared payment event handlers ─────────────────────────────────────────────
async def _on_payment_success(
    db:         AsyncSession,
    provider:   str,
    provider_id:str,
    order_id:   Optional[int],
    raw:        dict,
) -> None:
    """Called by all three webhook handlers on successful payment."""
    if not order_id:
        return

    # Update payment record
    r = await db.execute(
        select(Payment).where(
            Payment.order_id == order_id,
            Payment.provider == provider,
        )
    )
    payment = r.scalar_one_or_none()
    if payment:
        payment.status       = "paid"
        payment.raw_response = raw

    # Update order
    r2    = await db.execute(select(Order).where(Order.id == order_id))
    order = r2.scalar_one_or_none()
    if not order:
        return

    old_status    = order.status
    order.payment_status = "paid"
    order.status         = "pending_shipment"
    db.add(OrderStatusLog(
        order_id    = order_id,
        from_status = old_status,
        to_status   = "pending_shipment",
        note        = f"Payment confirmed via {provider}",
    ))


async def _on_payment_failed(
    db:         AsyncSession,
    provider:   str,
    provider_id:str,
    order_id:   Optional[int],
    raw:        dict,
    reason:     str,
) -> None:
    """Called by all three webhook handlers on failed payment."""
    if not order_id:
        return

    r = await db.execute(
        select(Payment).where(
            Payment.order_id == order_id,
            Payment.provider == provider,
        )
    )
    payment = r.scalar_one_or_none()
    if payment:
        payment.status       = "failed"
        payment.raw_response = raw

    r2    = await db.execute(select(Order).where(Order.id == order_id))
    order = r2.scalar_one_or_none()
    if not order:
        return

    order.payment_status = "failed"

    # Queue payment-failed email (dedup: max 1 per order)
    email = order.guest_email
    if not email and order.user_id:
        from app.models.user import User
        ru  = await db.execute(select(User).where(User.id == order.user_id))
        usr = ru.scalar_one_or_none()
        email = usr.email if usr else None

    if email:
        retry_url = f"{settings.FRONTEND_URL}/checkout/retry?order_id={order_id}"
        from app.tasks.email_tasks import send_payment_failed
        send_payment_failed.delay(
            order_id      = order_id,
            email         = email,
            customer_name = (order.shipping_address or {}).get("full_name", ""),
            fail_reason   = reason,
            retry_url     = retry_url,
            language      = order.language_code,
        )


# ── Refunds ───────────────────────────────────────────────────────────────────
async def process_refund(
    db:       AsyncSession,
    order_id: int,
    amount:   Optional[float],
    reason:   Optional[str],
    admin_id: Optional[int],
) -> dict:
    r = await db.execute(
        select(Payment).where(
            Payment.order_id == order_id,
            Payment.status   == "paid",
        )
    )
    payment = r.scalar_one_or_none()
    if not payment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No paid payment found for this order")

    refund_amount = amount or float(payment.amount)

    if payment.provider == "stripe":
        result = await _stripe_refund(payment.provider_payment_id, refund_amount)
    elif payment.provider == "paypal":
        result = await _paypal_refund(payment.provider_payment_id, refund_amount)
    elif payment.provider == "airwallex":
        result = await _airwallex_refund(payment.provider_payment_id, refund_amount, order_id, reason)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unknown provider: {payment.provider}")

    refund = Refund(
        payment_id         = payment.id,
        provider_refund_id = result.get("id"),
        amount             = refund_amount,
        reason             = reason,
        status             = "completed",
        processed_by       = admin_id,
    )
    db.add(refund)

    # Update order status
    r2    = await db.execute(select(Order).where(Order.id == order_id))
    order = r2.scalar_one_or_none()
    if order:
        old = order.status
        order.status         = "refunded"
        order.payment_status = "refunded"
        db.add(OrderStatusLog(order_id=order_id, from_status=old, to_status="refunded",
                               note=f"Refunded ${refund_amount:.2f} via {payment.provider}"))

    # Queue refund email
    from app.tasks.email_tasks import send_order_refunded
    email = order.guest_email if order else None
    if not email and order and order.user_id:
        from app.models.user import User
        ru  = await db.execute(select(User).where(User.id == order.user_id))
        usr = ru.scalar_one_or_none()
        email = usr.email if usr else None
    if email and order:
        send_order_refunded.delay(
            order_id      = order_id,
            email         = email,
            customer_name = (order.shipping_address or {}).get("full_name", ""),
            refund_amount = f"{refund_amount:.2f}",
            language      = order.language_code,
        )

    return {"refunded": True, "amount": refund_amount, "provider": payment.provider}


async def _stripe_refund(payment_intent_id: str, amount: float) -> dict:
    try:
        r = stripe.Refund.create(
            payment_intent = payment_intent_id,
            amount         = int(round(amount * 100)),
        )
        return {"id": r["id"]}
    except stripe.error.StripeError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Stripe refund error: {e.user_message}")


async def _paypal_refund(capture_id: str, amount: float) -> dict:
    token = await _paypal_access_token()
    base  = _paypal_base()
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{base}/v2/payments/captures/{capture_id}/refund",
            json    = {"amount": {"currency_code": "USD", "value": f"{amount:.2f}"}},
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        r.raise_for_status()
        return r.json()


async def _airwallex_refund(
    payment_intent_id: str,
    amount: float,
    order_id: int,
    reason: Optional[str] = None,
) -> dict:
    token = await _awx_access_token()
    base  = _awx_base()
    amount_value = float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    request_body = {
        "amount": amount_value,
        "currency": "USD",
        "merchant_order_id": str(order_id),
        "request_id": str(uuid.uuid4()),
    }
    if reason:
        request_body["reason"] = reason
    # Airwallex accepts refund by payment_intent_id or payment_attempt_id.
    if payment_intent_id.startswith("att_"):
        request_body["payment_attempt_id"] = payment_intent_id
    else:
        request_body["payment_intent_id"] = payment_intent_id

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{base}/api/v1/pa/refunds/create",
            json    = request_body,
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        if r.status_code >= 400:
            try:
                err = r.json()
            except Exception:
                err = {"message": r.text}
            logger.error(
                "airwallex refund failed status=%s payment_id=%s order_id=%s payload=%s error=%s",
                r.status_code, payment_intent_id, order_id, request_body, err,
            )
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Airwallex refund error: {err}")
        return r.json()
