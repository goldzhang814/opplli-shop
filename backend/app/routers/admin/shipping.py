"""
Admin Shipping & Tax Router
============================
Shipping Regions:
  GET  /api/v1/admin/shipping/regions
  PUT  /api/v1/admin/shipping/regions/{id}
  POST /api/v1/admin/shipping/regions

Zones:
  GET  /api/v1/admin/shipping/zones
  POST /api/v1/admin/shipping/zones
  PUT  /api/v1/admin/shipping/zones/{id}

Rules:
  GET  /api/v1/admin/shipping/rules
  POST /api/v1/admin/shipping/rules
  PUT  /api/v1/admin/shipping/rules/{id}

Carriers:
  GET    /api/v1/admin/carriers
  POST   /api/v1/admin/carriers
  PUT    /api/v1/admin/carriers/{id}
  DELETE /api/v1/admin/carriers/{id}

Tax:
  GET  /api/v1/admin/tax-rules
  POST /api/v1/admin/tax-rules
  PUT  /api/v1/admin/tax-rules/{id}
  DELETE /api/v1/admin/tax-rules/{id}
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.database import get_db
from app.core.dependencies import require_permission
from app.models.admin import Admin
from app.models.shipping import (
    ShippingRegion, ShippingZone, ShippingZoneRegion,
    ShippingRule, LogisticsCarrier,
)
from app.models.tax import TaxRule

router = APIRouter(prefix="/admin", tags=["Admin — Shipping & Tax"])


# ── Pydantic schemas (inline) ─────────────────────────────────────────────────
class ShippingRegionUpdate(BaseModel):
    enabled: bool


class ShippingRegionCreate(BaseModel):
    country_code: str
    state_code:   Optional[str] = None
    enabled:      bool          = True


class ZoneCreate(BaseModel):
    name:          str
    country_codes: list[str] = []


class ZoneUpdate(BaseModel):
    name:          Optional[str]       = None
    country_codes: Optional[list[str]] = None


class ShippingRuleCreate(BaseModel):
    zone_id:                 int
    shipping_fee:            float
    free_shipping_threshold: float
    is_active:               bool = True


class ShippingRuleUpdate(BaseModel):
    shipping_fee:            Optional[float] = None
    free_shipping_threshold: Optional[float] = None
    is_active:               Optional[bool]  = None


class CarrierCreate(BaseModel):
    name:                   str
    code:                   str
    tracking_url_template:  Optional[str]       = None
    applicable_countries:   Optional[list[str]] = None
    is_active:              bool                = True


class CarrierUpdate(BaseModel):
    name:                   Optional[str]       = None
    tracking_url_template:  Optional[str]       = None
    applicable_countries:   Optional[list[str]] = None
    is_active:              Optional[bool]      = None


class TaxRuleCreate(BaseModel):
    country_code:      str
    state_code:        Optional[str]  = None
    tax_rate:          float
    tax_name:          str            = "Sales Tax"
    apply_to_shipping: bool           = False
    category_id:       Optional[int]  = None
    is_active:         bool           = True


class TaxRuleUpdate(BaseModel):
    tax_rate:          Optional[float] = None
    tax_name:          Optional[str]   = None
    apply_to_shipping: Optional[bool]  = None
    is_active:         Optional[bool]  = None


# ── Shipping Regions ──────────────────────────────────────────────────────────
@router.get("/shipping/regions")
async def list_regions(
    country_code: Optional[str] = None,
    _:  Admin        = Depends(require_permission("shipping")),
    db: AsyncSession = Depends(get_db),
):
    q = select(ShippingRegion).order_by(
        ShippingRegion.country_code, ShippingRegion.state_code
    )
    if country_code:
        q = q.where(ShippingRegion.country_code == country_code.upper())
    r = await db.execute(q)
    return r.scalars().all()


@router.post("/shipping/regions", status_code=201)
async def create_region(
    req: ShippingRegionCreate,
    _:   Admin        = Depends(require_permission("shipping")),
    db:  AsyncSession = Depends(get_db),
):
    region = ShippingRegion(**req.model_dump())
    db.add(region)
    await db.flush()
    return region


@router.put("/shipping/regions/{region_id}")
async def update_region(
    region_id: int,
    req:       ShippingRegionUpdate,
    _:         Admin        = Depends(require_permission("shipping")),
    db:        AsyncSession = Depends(get_db),
):
    r = await db.execute(select(ShippingRegion).where(ShippingRegion.id == region_id))
    region = r.scalar_one_or_none()
    if not region:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Region not found")
    region.enabled = req.enabled
    return region


# ── Shipping Zones ────────────────────────────────────────────────────────────
@router.get("/shipping/zones")
async def list_zones(
    _:  Admin        = Depends(require_permission("shipping")),
    db: AsyncSession = Depends(get_db),
):
    q = select(ShippingZone).options(
        selectinload(ShippingZone.country_mappings),
        selectinload(ShippingZone.rules),
    )
    zones = (await db.execute(q)).scalars().all()
    return [
        {
            "id":             z.id,
            "name":           z.name,
            "country_codes":  [m.country_code for m in z.country_mappings],
            "rules":          [
                {
                    "id":                      r.id,
                    "shipping_fee":            float(r.shipping_fee),
                    "free_shipping_threshold": float(r.free_shipping_threshold),
                    "is_active":               r.is_active,
                }
                for r in z.rules
            ],
        }
        for z in zones
    ]


@router.post("/shipping/zones", status_code=201)
async def create_zone(
    req: ZoneCreate,
    _:   Admin        = Depends(require_permission("shipping")),
    db:  AsyncSession = Depends(get_db),
):
    zone = ShippingZone(name=req.name)
    db.add(zone)
    await db.flush()
    for cc in req.country_codes:
        db.add(ShippingZoneRegion(zone_id=zone.id, country_code=cc.upper()))
    await db.flush()
    return {"id": zone.id, "name": zone.name}


@router.put("/shipping/zones/{zone_id}")
async def update_zone(
    zone_id: int,
    req:     ZoneUpdate,
    _:       Admin        = Depends(require_permission("shipping")),
    db:      AsyncSession = Depends(get_db),
):
    r    = await db.execute(select(ShippingZone).where(ShippingZone.id == zone_id))
    zone = r.scalar_one_or_none()
    if not zone:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Zone not found")
    if req.name:
        zone.name = req.name
    if req.country_codes is not None:
        # Replace all mappings
        from sqlalchemy import delete
        await db.execute(
            delete(ShippingZoneRegion).where(ShippingZoneRegion.zone_id == zone_id)
        )
        for cc in req.country_codes:
            db.add(ShippingZoneRegion(zone_id=zone_id, country_code=cc.upper()))
    return {"id": zone.id, "name": zone.name}


# ── Shipping Rules ────────────────────────────────────────────────────────────
@router.get("/shipping/rules")
async def list_rules(
    _:  Admin        = Depends(require_permission("shipping")),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(ShippingRule).order_by(ShippingRule.zone_id))
    return r.scalars().all()


@router.post("/shipping/rules", status_code=201)
async def create_rule(
    req: ShippingRuleCreate,
    _:   Admin        = Depends(require_permission("shipping")),
    db:  AsyncSession = Depends(get_db),
):
    rule = ShippingRule(**req.model_dump())
    db.add(rule)
    await db.flush()
    return rule


@router.put("/shipping/rules/{rule_id}")
async def update_rule(
    rule_id: int,
    req:     ShippingRuleUpdate,
    _:       Admin        = Depends(require_permission("shipping")),
    db:      AsyncSession = Depends(get_db),
):
    r    = await db.execute(select(ShippingRule).where(ShippingRule.id == rule_id))
    rule = r.scalar_one_or_none()
    if not rule:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rule not found")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(rule, k, v)
    return rule


# ── Carriers ──────────────────────────────────────────────────────────────────
@router.get("/carriers")
async def list_carriers(
    _:  Admin        = Depends(require_permission("carriers")),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(LogisticsCarrier).order_by(LogisticsCarrier.name))
    return r.scalars().all()


@router.post("/carriers", status_code=201)
async def create_carrier(
    req: CarrierCreate,
    _:   Admin        = Depends(require_permission("carriers")),
    db:  AsyncSession = Depends(get_db),
):
    carrier = LogisticsCarrier(**req.model_dump())
    db.add(carrier)
    await db.flush()
    return carrier


@router.put("/carriers/{carrier_id}")
async def update_carrier(
    carrier_id: int,
    req:        CarrierUpdate,
    _:          Admin        = Depends(require_permission("carriers")),
    db:         AsyncSession = Depends(get_db),
):
    r       = await db.execute(select(LogisticsCarrier).where(LogisticsCarrier.id == carrier_id))
    carrier = r.scalar_one_or_none()
    if not carrier:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Carrier not found")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(carrier, k, v)
    return carrier


@router.delete("/carriers/{carrier_id}", status_code=204)
async def delete_carrier(
    carrier_id: int,
    _:          Admin        = Depends(require_permission("carriers")),
    db:         AsyncSession = Depends(get_db),
):
    r       = await db.execute(select(LogisticsCarrier).where(LogisticsCarrier.id == carrier_id))
    carrier = r.scalar_one_or_none()
    if not carrier:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Carrier not found")
    await db.delete(carrier)


# ── Tax Rules ─────────────────────────────────────────────────────────────────
@router.get("/tax-rules")
async def list_tax_rules(
    _:  Admin        = Depends(require_permission("tax")),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(
        select(TaxRule).order_by(TaxRule.country_code, TaxRule.state_code)
    )
    return r.scalars().all()


@router.post("/tax-rules", status_code=201)
async def create_tax_rule(
    req: TaxRuleCreate,
    _:   Admin        = Depends(require_permission("tax")),
    db:  AsyncSession = Depends(get_db),
):
    rule = TaxRule(**req.model_dump())
    db.add(rule)
    await db.flush()
    return rule


@router.put("/tax-rules/{rule_id}")
async def update_tax_rule(
    rule_id: int,
    req:     TaxRuleUpdate,
    _:       Admin        = Depends(require_permission("tax")),
    db:      AsyncSession = Depends(get_db),
):
    r    = await db.execute(select(TaxRule).where(TaxRule.id == rule_id))
    rule = r.scalar_one_or_none()
    if not rule:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tax rule not found")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(rule, k, v)
    return rule


@router.delete("/tax-rules/{rule_id}", status_code=204)
async def delete_tax_rule(
    rule_id: int,
    _:       Admin        = Depends(require_permission("tax")),
    db:      AsyncSession = Depends(get_db),
):
    r    = await db.execute(select(TaxRule).where(TaxRule.id == rule_id))
    rule = r.scalar_one_or_none()
    if not rule:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tax rule not found")
    await db.delete(rule)
