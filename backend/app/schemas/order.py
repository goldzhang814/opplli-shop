from __future__ import annotations
from typing import Optional, Any
from pydantic import BaseModel


class OrderItemOut(BaseModel):
    id:            int
    sku_id:        Optional[int]
    product_name:  str
    sku_code:      str
    variant_attrs: Optional[dict]
    quantity:      int
    unit_price:    float
    subtotal:      float
    product_image: Optional[str]
    model_config = {"from_attributes": True}


class ShipmentOut(BaseModel):
    carrier_id:   int
    carrier_name: Optional[str] = None
    tracking_no:  str
    tracking_url: Optional[str] = None
    shipped_at:   Any
    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id:                 int
    order_no:           str
    status:             str
    subtotal:           float
    shipping_fee:       float
    tax_amount:         float
    discount_amount:    float
    total_amount:       float
    payment_method:     Optional[str]
    payment_status:     str
    coupon_code:        Optional[str]
    shipping_address:   Optional[dict]
    shipping_zone_name: Optional[str]
    channel_ref:        Optional[str]
    language_code:      str
    customer_note:      Optional[str]
    admin_note:         Optional[str]
    created_at:         Any
    items:              list[OrderItemOut] = []
    shipment:           Optional[ShipmentOut] = None
    model_config = {"from_attributes": True}


class OrderListItem(BaseModel):
    id:             int
    order_no:       str
    status:         str
    total_amount:   float
    payment_method: Optional[str]
    payment_status: str
    item_count:     int
    created_at:     Any
    model_config = {"from_attributes": True}


class PaginatedOrders(BaseModel):
    items:  list[OrderListItem]
    total:  int
    page:   int
    pages:  int


class OrderStatusUpdate(BaseModel):
    status: str
    note:   Optional[str] = None


class ShipOrderRequest(BaseModel):
    carrier_id:  int
    tracking_no: str
    note:        Optional[str] = None


class RefundRequest(BaseModel):
    amount: Optional[float] = None
    reason: Optional[str]  = None


class AdminOrderUpdate(BaseModel):
    """Admin can update status and/or leave an internal note in one call."""
    status:     Optional[str] = None
    admin_note: Optional[str] = None
