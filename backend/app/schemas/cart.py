from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ── Cart items ────────────────────────────────────────────────────────────────
class CartItemIn(BaseModel):
    sku_id:   int
    quantity: int = Field(ge=1, le=99)


class CartItemOut(BaseModel):
    sku_id:        int
    sku_code:      str
    product_id:    int
    product_name:  str
    product_slug:  str
    variant_attrs: Optional[dict]
    quantity:      int
    unit_price:    float
    compare_price: Optional[float]
    subtotal:      float
    stock:         int
    cover_image:   Optional[str]
    free_shipping: bool


class CartOut(BaseModel):
    items:       list[CartItemOut]
    item_count:  int
    subtotal:    float
    guest_token: Optional[str] = None


# ── Checkout address ──────────────────────────────────────────────────────────
class CheckoutAddress(BaseModel):
    full_name:     str
    phone:         Optional[str]  = None
    country_code:  str
    state_code:    Optional[str]  = None
    state_name:    Optional[str]  = None
    city:          str
    address_line1: str
    address_line2: Optional[str]  = None
    postal_code:   str


# ── Coupon validation ─────────────────────────────────────────────────────────
class CouponValidateRequest(BaseModel):
    code:        str
    order_total: float = Field(ge=0)


class CouponValidateResponse(BaseModel):
    valid:           bool
    code:            Optional[str]   = None
    type:            Optional[str]   = None   # percent | fixed | free_shipping
    value:           Optional[float] = None
    discount_amount: Optional[float] = None
    message:         Optional[str]   = None   # error reason when invalid


# ── Shipping estimate ─────────────────────────────────────────────────────────
class ShippingEstimateRequest(BaseModel):
    country_code: str
    state_code:   Optional[str] = None
    subtotal:     float         = Field(ge=0)


class ShippingEstimateResponse(BaseModel):
    deliverable:             bool
    zone_name:               Optional[str]   = None
    shipping_fee:            float           = 0.0
    free_shipping_threshold: Optional[float] = None
    remaining_for_free:      Optional[float] = None
    message:                 Optional[str]   = None


# ── Tax estimate ──────────────────────────────────────────────────────────────
class TaxEstimateResponse(BaseModel):
    tax_rate:          float
    tax_name:          str
    tax_amount:        float
    apply_to_shipping: bool


# ── Checkout preview ──────────────────────────────────────────────────────────
class CheckoutPreviewRequest(BaseModel):
    address:     CheckoutAddress
    coupon_code: Optional[str] = None
    channel_ref: Optional[str] = None


class CheckoutPreviewResponse(BaseModel):
    subtotal:        float
    shipping_fee:    float
    tax_amount:      float
    discount_amount: float
    total_amount:    float
    coupon:          Optional[CouponValidateResponse] = None
    shipping:        Optional[ShippingEstimateResponse] = None
    tax:             Optional[TaxEstimateResponse]     = None
    free_shipping_threshold: Optional[float] = None
    remaining_for_free:      Optional[float] = None


# ── Place order ───────────────────────────────────────────────────────────────
class PlaceOrderRequest(BaseModel):
    address:        CheckoutAddress
    payment_method: str = Field(pattern="^(stripe|paypal|airwallex)$")
    coupon_code:    Optional[str] = None
    channel_ref:    Optional[str] = None
    customer_note:  Optional[str] = None
    language_code:  str           = "en"
    save_address:   bool          = False


class PlaceOrderResponse(BaseModel):
    order_id:        int
    order_no:        str
    total_amount:    float
    payment_method:  str
    client_secret:   Optional[str] = None   # Stripe
    approval_url:    Optional[str] = None   # PayPal redirect
    payment_intent_id: Optional[str] = None # Airwallex
