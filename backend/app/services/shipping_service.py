"""
Shipping & Tax Service
======================
Implements the 3-layer shipping logic:
  shipping_regions → check deliverability (country + state)
  shipping_zones   → find zone by country
  shipping_rules   → get fee + free_shipping_threshold

Tax: country + optional state lookup, supports apply_to_shipping flag.
"""
from __future__ import annotations
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shipping import ShippingRegion, ShippingZone, ShippingZoneRegion, ShippingRule
from app.models.tax import TaxRule
from app.schemas.cart import ShippingEstimateResponse, TaxEstimateResponse


async def check_deliverable(
    db:           AsyncSession,
    country_code: str,
    state_code:   Optional[str] = None,
) -> bool:
    """Check if the given country/state combination is enabled for shipping."""
    if state_code:
        # State-level check (US)
        r = await db.execute(
            select(ShippingRegion).where(
                ShippingRegion.country_code == country_code,
                ShippingRegion.state_code   == state_code,
            )
        )
        region = r.scalar_one_or_none()
        if region:
            return region.enabled
        # Fallback: check country-level (state_code IS NULL)
    # Country-level check
    r = await db.execute(
        select(ShippingRegion).where(
            ShippingRegion.country_code == country_code,
            ShippingRegion.state_code   == None,
        )
    )
    region = r.scalar_one_or_none()
    if region:
        return region.enabled
    # If no record found at all → not configured → not deliverable
    return False


async def get_shipping_estimate(
    db:           AsyncSession,
    country_code: str,
    state_code:   Optional[str],
    subtotal:     float,
) -> ShippingEstimateResponse:
    """
    Full shipping calculation:
    1. Check deliverability
    2. Find zone by country
    3. Find rule for zone
    4. Apply free-shipping threshold
    """
    # Step 1: deliverability
    deliverable = await check_deliverable(db, country_code, state_code)
    if not deliverable:
        return ShippingEstimateResponse(
            deliverable = False,
            message     = "Sorry, we don't ship to this region yet.",
        )

    # Step 2: find zone
    r = await db.execute(
        select(ShippingZoneRegion)
        .where(ShippingZoneRegion.country_code == country_code)
    )
    zone_region = r.scalar_one_or_none()

    if not zone_region:
        # Fallback: try "International" zone (zone_id=5 by convention) or any active rule
        r2 = await db.execute(
            select(ShippingRule).where(ShippingRule.is_active == True).order_by(ShippingRule.id.desc())
        )
        rule = r2.scalar_one_or_none()
        zone_name = "International"
    else:
        # Step 3: find rule for zone
        r3 = await db.execute(
            select(ShippingRule).where(
                ShippingRule.zone_id   == zone_region.zone_id,
                ShippingRule.is_active == True,
            )
        )
        rule = r3.scalar_one_or_none()

        r4 = await db.execute(
            select(ShippingZone).where(ShippingZone.id == zone_region.zone_id)
        )
        zone = r4.scalar_one_or_none()
        zone_name = zone.name if zone else "Standard"

    if not rule:
        return ShippingEstimateResponse(
            deliverable = False,
            message     = "No shipping rate configured for this region.",
        )

    # Step 4: apply threshold
    threshold = float(rule.free_shipping_threshold)
    fee       = 0.0 if subtotal >= threshold else float(rule.shipping_fee)
    remaining = max(0.0, round(threshold - subtotal, 2)) if fee > 0 else None

    return ShippingEstimateResponse(
        deliverable             = True,
        zone_name               = zone_name,
        shipping_fee            = fee,
        free_shipping_threshold = threshold,
        remaining_for_free      = remaining,
    )


async def get_shipping_rule_for_country(
    db:           AsyncSession,
    country_code: str,
) -> Optional[ShippingRule]:
    """Returns the ShippingRule object for a country (used by checkout)."""
    r = await db.execute(
        select(ShippingZoneRegion).where(ShippingZoneRegion.country_code == country_code)
    )
    zr = r.scalar_one_or_none()
    if not zr:
        return None
    r2 = await db.execute(
        select(ShippingRule).where(
            ShippingRule.zone_id   == zr.zone_id,
            ShippingRule.is_active == True,
        )
    )
    return r2.scalar_one_or_none()


# ── Tax ───────────────────────────────────────────────────────────────────────
async def get_tax_estimate(
    db:           AsyncSession,
    country_code: str,
    state_code:   Optional[str],
    subtotal:     float,
    shipping_fee: float = 0.0,
    category_id:  Optional[int] = None,
) -> TaxEstimateResponse:
    """
    Tax lookup priority:
    1. country + state + category  (most specific)
    2. country + state
    3. country + category
    4. country only
    """
    candidates = []

    # Build lookup order
    if state_code and category_id:
        candidates.append((country_code, state_code, category_id))
    if state_code:
        candidates.append((country_code, state_code, None))
    if category_id:
        candidates.append((country_code, None, category_id))
    candidates.append((country_code, None, None))

    rule = None
    for cc, sc, cat_id in candidates:
        q = select(TaxRule).where(
            TaxRule.country_code == cc,
            TaxRule.is_active    == True,
        )
        if sc:
            q = q.where(TaxRule.state_code == sc)
        else:
            q = q.where(TaxRule.state_code == None)
        if cat_id:
            q = q.where(TaxRule.category_id == cat_id)
        else:
            q = q.where(TaxRule.category_id == None)

        r    = await db.execute(q)
        rule = r.scalar_one_or_none()
        if rule:
            break

    if not rule:
        return TaxEstimateResponse(
            tax_rate=0.0, tax_name="", tax_amount=0.0, apply_to_shipping=False
        )

    taxable = subtotal + (shipping_fee if rule.apply_to_shipping else 0.0)
    amount  = round(taxable * float(rule.tax_rate), 2)

    return TaxEstimateResponse(
        tax_rate          = float(rule.tax_rate),
        tax_name          = rule.tax_name,
        tax_amount        = amount,
        apply_to_shipping = rule.apply_to_shipping,
    )
