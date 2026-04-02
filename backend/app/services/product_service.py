"""
Product Service
===============
Handles: categories, products CRUD, SKUs, images, inventory,
         reviews (submit + moderation + auto-approve), wishlist, search.
"""
from __future__ import annotations
import math
from typing import Optional
from datetime import datetime, timezone

from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select, func, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import (
    Category, Product, ProductSku, ProductImage,
    InventoryLog, ProductReview, ReviewMedia, Wishlist,
)
from app.models.content import SiteSetting
from app.models.order import Order, OrderItem
from app.schemas.product import (
    CategoryCreate, CategoryUpdate,
    ProductCreate, ProductUpdate,
    SkuCreate, SkuUpdate,
    InventoryAdjust, ReviewSubmit, ReviewModerate,
    ProductImageOut,
)
from app.core.storage import upload_file, resolve_url, delete_file, ALLOWED_IMAGE_MIMES, ALLOWED_VIDEO_MIMES
from slugify import slugify


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────
async def _get_auto_approve_threshold(db: AsyncSession) -> int:
    r = await db.execute(
        select(SiteSetting).where(SiteSetting.key == "review_auto_approve_threshold")
    )
    s = r.scalar_one_or_none()
    try:
        return int(s.value) if s and s.value else 3
    except (ValueError, TypeError):
        return 3


def _resolve_images(images: list[ProductImage]) -> list[ProductImageOut]:
    return [
        ProductImageOut(
            id=img.id,
            url=resolve_url(img.url, img.storage_type),
            alt_text=img.alt_text,
            sort_order=img.sort_order,
            storage_type=img.storage_type,
        )
        for img in images
    ]


def _resolve_review_media(media: list[ReviewMedia]) -> list[dict]:
    sorted_media = sorted(media, key=lambda m: m.sort_order)
    return [
        {
            "id":           m.id,
            "url":          resolve_url(m.url, m.storage_type),
            "storage_type": m.storage_type,
            "media_type":   m.media_type,
            "sort_order":   m.sort_order,
        }
        for m in sorted_media
    ]


def _review_dict(review: ProductReview) -> dict:
    return {
        "id":                   review.id,
        "product_id":           review.product_id,
        "user_id":              review.user_id,
        "rating":               review.rating,
        "content":              review.content,
        "status":               review.status,
        "reviewer_name":        review.reviewer_name,
        "is_verified_purchase": review.is_verified_purchase,
        "media":                _resolve_review_media(review.media),
        "created_at":           review.created_at,
    }


def _product_list_item(p: Product) -> dict:
    prices     = [s.price for s in p.skus if s.is_active]
    cover      = None
    if p.images:
        first = p.images[0]
        cover = resolve_url(first.url, first.storage_type)
    return {
        "id":           p.id,
        "name":         p.name,
        "slug":         p.slug,
        "is_published": p.is_published,
        "rating_avg":   p.rating_avg,
        "rating_count": p.rating_count,
        "category_id":  p.category_id,
        "category_name":p.category.name if p.category else None,
        "min_price":    min(prices) if prices else None,
        "max_price":    max(prices) if prices else None,
        "cover_image":  cover,
    }


async def _unique_slug(db: AsyncSession, base: str, exclude_id: Optional[int] = None) -> str:
    slug = slugify(base)
    q    = select(Product).where(Product.slug == slug)
    if exclude_id:
        q = q.where(Product.id != exclude_id)
    if not (await db.execute(q)).scalar_one_or_none():
        return slug
    counter = 1
    while True:
        candidate = f"{slug}-{counter}"
        q2 = select(Product).where(Product.slug == candidate)
        if exclude_id:
            q2 = q2.where(Product.id != exclude_id)
        if not (await db.execute(q2)).scalar_one_or_none():
            return candidate
        counter += 1


# ────────────────────────────────────────────────────────────────────────────
# Categories
# ────────────────────────────────────────────────────────────────────────────
async def list_categories(db: AsyncSession, active_only: bool = True) -> list[Category]:
    q = select(Category)
    if active_only:
        q = q.where(Category.is_active == True)
    q = q.order_by(Category.sort_order, Category.name)
    return (await db.execute(q)).scalars().all()


async def create_category(db: AsyncSession, req: CategoryCreate) -> Category:
    slug = slugify(req.slug or req.name)
    cat  = Category(**req.model_dump(exclude={"slug"}), slug=slug)
    db.add(cat)
    await db.flush()
    return cat


async def update_category(db: AsyncSession, cat_id: int, req: CategoryUpdate) -> Category:
    r   = await db.execute(select(Category).where(Category.id == cat_id))
    cat = r.scalar_one_or_none()
    if not cat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(cat, k, v)
    return cat


async def delete_category(db: AsyncSession, cat_id: int) -> None:
    r   = await db.execute(select(Category).where(Category.id == cat_id))
    cat = r.scalar_one_or_none()
    if not cat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    await db.delete(cat)


# ────────────────────────────────────────────────────────────────────────────
# Products
# ────────────────────────────────────────────────────────────────────────────
async def list_products(
    db:          AsyncSession,
    page:        int            = 1,
    limit:       int            = 20,
    category_id: Optional[int]  = None,
    search:      Optional[str]  = None,
    published_only: bool        = True,
    sort:        str            = "created_desc",
) -> dict:
    q = (
        select(Product)
        .options(
            selectinload(Product.skus),
            selectinload(Product.images),
            selectinload(Product.category),
        )
    )
    if published_only:
        q = q.where(Product.is_published == True)
    if category_id:
        q = q.where(Product.category_id == category_id)
    if search:
        like = f"%{search}%"
        q    = q.where(or_(Product.name.ilike(like), Product.short_desc.ilike(like)))

    sort_map = {
        "created_desc": Product.created_at.desc(),
        "created_asc":  Product.created_at.asc(),
        "name_asc":     Product.name.asc(),
        "rating_desc":  Product.rating_avg.desc(),
    }
    q = q.order_by(sort_map.get(sort, Product.created_at.desc()))

    # Count
    count_q  = select(func.count()).select_from(q.subquery())
    total    = (await db.execute(count_q)).scalar_one()
    pages    = max(1, math.ceil(total / limit))
    offset   = (page - 1) * limit

    items    = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return {
        "items": [_product_list_item(p) for p in items],
        "total": total, "page": page, "pages": pages, "limit": limit,
    }


async def get_product_by_slug(db: AsyncSession, slug: str, published_only: bool = True) -> Product:
    q = (
        select(Product)
        .where(Product.slug == slug)
        .options(
            selectinload(Product.skus),
            selectinload(Product.images),
            selectinload(Product.category),
        )
    )
    if published_only:
        q = q.where(Product.is_published == True)
    p = (await db.execute(q)).scalar_one_or_none()
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return p


async def get_product_by_id(db: AsyncSession, product_id: int) -> Product:
    q = (
        select(Product)
        .where(Product.id == product_id)
        .options(
            selectinload(Product.skus),
            selectinload(Product.images),
            selectinload(Product.category),
        )
    )
    p = (await db.execute(q)).scalar_one_or_none()
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return p


async def create_product(db: AsyncSession, req: ProductCreate) -> Product:
    slug = await _unique_slug(db, req.slug or req.name)
    product = Product(
        name            = req.name,
        slug            = slug,
        description     = req.description,
        short_desc      = req.short_desc,
        category_id     = req.category_id,
        is_published    = req.is_published,
        seo_title       = req.seo_title,
        seo_description = req.seo_description,
        seo_slug        = req.seo_slug,
        og_image        = req.og_image,
    )
    db.add(product)
    await db.flush()

    for sku_data in req.skus:
        sku = ProductSku(product_id=product.id, **sku_data.model_dump())
        db.add(sku)

    await db.flush()
    return await get_product_by_id(db, product.id)


async def update_product(db: AsyncSession, product_id: int, req: ProductUpdate) -> Product:
    product = await get_product_by_id(db, product_id)
    data    = req.model_dump(exclude_none=True)
    if "slug" in data:
        data["slug"] = await _unique_slug(db, data["slug"], exclude_id=product_id)
    for k, v in data.items():
        setattr(product, k, v)
    return product


async def delete_product(db: AsyncSession, product_id: int) -> None:
    product = await get_product_by_id(db, product_id)
    # Delete associated media files from storage
    for img in product.images:
        await delete_file(img.url, img.storage_type)
    await db.delete(product)


async def publish_product(db: AsyncSession, product_id: int, publish: bool) -> Product:
    product = await get_product_by_id(db, product_id)
    if publish and not product.skus:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Cannot publish a product with no SKUs")
    product.is_published = publish
    return product


# ────────────────────────────────────────────────────────────────────────────
# SKUs
# ────────────────────────────────────────────────────────────────────────────
async def create_sku(db: AsyncSession, product_id: int, req: SkuCreate) -> ProductSku:
    # Check sku_code uniqueness
    r = await db.execute(select(ProductSku).where(ProductSku.sku_code == req.sku_code))
    if r.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, f"SKU code '{req.sku_code}' already exists")
    sku = ProductSku(product_id=product_id, **req.model_dump())
    db.add(sku)
    await db.flush()
    return sku


async def update_sku(db: AsyncSession, sku_id: int, req: SkuUpdate) -> ProductSku:
    r   = await db.execute(select(ProductSku).where(ProductSku.id == sku_id))
    sku = r.scalar_one_or_none()
    if not sku:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "SKU not found")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(sku, k, v)
    return sku


async def delete_sku(db: AsyncSession, sku_id: int) -> None:
    r   = await db.execute(select(ProductSku).where(ProductSku.id == sku_id))
    sku = r.scalar_one_or_none()
    if not sku:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "SKU not found")
    await db.delete(sku)


# ────────────────────────────────────────────────────────────────────────────
# Product Images
# ────────────────────────────────────────────────────────────────────────────
async def upload_product_image(
    db:         AsyncSession,
    product_id: int,
    file:       UploadFile,
    alt_text:   Optional[str] = None,
) -> ProductImage:
    await get_product_by_id(db, product_id)   # validate exists

    result = await upload_file(file, folder=f"products/{product_id}", allowed_mimes=ALLOWED_IMAGE_MIMES)

    # Sort order = max existing + 1
    r          = await db.execute(
        select(func.max(ProductImage.sort_order)).where(ProductImage.product_id == product_id)
    )
    max_order  = r.scalar_one_or_none() or 0
    img = ProductImage(
        product_id   = product_id,
        url          = result["path"],
        storage_type = result["storage_type"],
        alt_text     = alt_text,
        sort_order   = max_order + 1,
    )
    db.add(img)
    await db.flush()
    return img


async def delete_product_image(db: AsyncSession, image_id: int) -> None:
    r   = await db.execute(select(ProductImage).where(ProductImage.id == image_id))
    img = r.scalar_one_or_none()
    if not img:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Image not found")
    await delete_file(img.url, img.storage_type)
    await db.delete(img)


async def reorder_images(db: AsyncSession, product_id: int, ordered_ids: list[int]) -> None:
    for pos, img_id in enumerate(ordered_ids):
        await db.execute(
            update(ProductImage)
            .where(ProductImage.id == img_id, ProductImage.product_id == product_id)
            .values(sort_order=pos)
        )


# ────────────────────────────────────────────────────────────────────────────
# Inventory
# ────────────────────────────────────────────────────────────────────────────
async def adjust_inventory(
    db:          AsyncSession,
    sku_id:      int,
    req:         InventoryAdjust,
    operator_id: Optional[int] = None,
) -> ProductSku:
    r   = await db.execute(select(ProductSku).where(ProductSku.id == sku_id))
    sku = r.scalar_one_or_none()
    if not sku:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "SKU not found")

    before = sku.stock
    after  = before + req.change_qty
    if after < 0:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            f"Cannot reduce stock below 0 (current: {before})")

    sku.stock = after
    log = InventoryLog(
        sku_id      = sku_id,
        change_qty  = req.change_qty,
        before_qty  = before,
        after_qty   = after,
        reason      = req.reason,
        reference_id= req.note,
        operator_id = operator_id,
    )
    db.add(log)
    return sku


async def get_inventory_logs(
    db:     AsyncSession,
    sku_id: Optional[int] = None,
    page:   int           = 1,
    limit:  int           = 50,
) -> dict:
    q = select(InventoryLog).order_by(InventoryLog.created_at.desc())
    if sku_id:
        q = q.where(InventoryLog.sku_id == sku_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"items": items, "total": total, "page": page, "pages": max(1, math.ceil(total / limit))}


async def get_low_stock_skus(db: AsyncSession) -> list[ProductSku]:
    q = (
        select(ProductSku)
        .where(
            ProductSku.is_active == True,
            ProductSku.stock <= ProductSku.low_stock_threshold,
        )
        .options(selectinload(ProductSku.product))
        .order_by(ProductSku.stock.asc())
    )
    return (await db.execute(q)).scalars().all()


# ────────────────────────────────────────────────────────────────────────────
# Reviews
# ────────────────────────────────────────────────────────────────────────────
async def _update_product_rating(db: AsyncSession, product_id: int) -> None:
    """Atomically recalculate rating_avg and rating_count from approved reviews."""
    r = await db.execute(
        select(
            func.avg(ProductReview.rating).label("avg"),
            func.count(ProductReview.id).label("cnt"),
        ).where(
            ProductReview.product_id == product_id,
            ProductReview.status     == "approved",
        )
    )
    row = r.one()
    await db.execute(
        update(Product)
        .where(Product.id == product_id)
        .values(
            rating_avg   = round(float(row.avg or 0), 2),
            rating_count = row.cnt or 0,
        )
    )


async def submit_review(
    db:         AsyncSession,
    user_id:    int,
    req:        ReviewSubmit,
    media_files:list[UploadFile] = [],
) -> ProductReview:
    if len(media_files) > 3:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Max 3 media files per review")

    # Must be a verified purchaser
    r = await db.execute(
        select(Order)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .join(ProductSku, ProductSku.id == OrderItem.sku_id)
        .where(
            Order.user_id          == user_id,
            Order.payment_status   == "paid",
            Order.status.in_(("pending_shipment", "shipped", "completed")),
            ProductSku.product_id  == req.product_id,
        )
    )
    order = r.scalar_one_or_none()
    is_verified = order is not None

    # Auto-approve threshold
    threshold = await _get_auto_approve_threshold(db)
    auto_approve = threshold > 0 and req.rating >= threshold
    review_status = "approved" if auto_approve else "pending"

    review = ProductReview(
        product_id           = req.product_id,
        user_id              = user_id,
        order_id             = req.order_id,
        rating               = req.rating,
        content              = req.content,
        reviewer_name        = req.reviewer_name,
        status               = review_status,
        is_verified_purchase = is_verified,
    )
    db.add(review)
    await db.flush()

    # Upload media
    for i, mf in enumerate(media_files[:3]):  # max 3 files per review
        allowed = ALLOWED_IMAGE_MIMES | ALLOWED_VIDEO_MIMES
        result  = await upload_file(mf, folder=f"reviews/{review.id}", allowed_mimes=allowed)
        db.add(ReviewMedia(
            review_id    = review.id,
            url          = result["path"],
            storage_type = result["storage_type"],
            media_type   = result["file_type"],
            sort_order   = i,
        ))

    if auto_approve:
        await _update_product_rating(db, req.product_id)

    return review


async def moderate_review(
    db:        AsyncSession,
    review_id: int,
    req:       ReviewModerate,
) -> ProductReview:
    r      = await db.execute(select(ProductReview).where(ProductReview.id == review_id))
    review = r.scalar_one_or_none()
    if not review:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")

    old_status = review.status
    if req.action == "approve":
        review.status = "approved"
    elif req.action == "reject":
        review.status        = "rejected"
        review.reject_reason = req.reject_reason
    else:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "action must be approve or reject")

    # Recalculate rating if status changed
    if old_status != review.status:
        await _update_product_rating(db, review.product_id)

    return review


async def list_reviews(
    db:         AsyncSession,
    product_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    page:       int           = 1,
    limit:      int           = 20,
) -> dict:
    q = select(ProductReview).options(selectinload(ProductReview.media))
    if product_id:
        q = q.where(ProductReview.product_id == product_id)
    if status_filter:
        q = q.where(ProductReview.status == status_filter)
    q     = q.order_by(ProductReview.created_at.desc())
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {
        "items": [_review_dict(review) for review in items],
        "total": total,
        "page": page,
        "pages": max(1, math.ceil(total / limit)),
    }


# ────────────────────────────────────────────────────────────────────────────
# Wishlist
# ────────────────────────────────────────────────────────────────────────────
async def get_wishlist(db: AsyncSession, user_id: int) -> list[dict]:
    q = (
        select(Wishlist)
        .where(Wishlist.user_id == user_id)
        .options(selectinload(Wishlist.product).selectinload(Product.skus),
                 selectinload(Wishlist.product).selectinload(Product.images))
    )
    items = (await db.execute(q)).scalars().all()
    result = []
    for w in items:
        p      = w.product
        prices = [s.price for s in p.skus if s.is_active]
        cover  = None
        if p.images:
            cover = resolve_url(p.images[0].url, p.images[0].storage_type)
        result.append({
            "product_id":   p.id,
            "product_name": p.name,
            "slug":         p.slug,
            "cover_image":  cover,
            "min_price":    min(prices) if prices else None,
        })
    return result


async def toggle_wishlist(db: AsyncSession, user_id: int, product_id: int) -> dict:
    r = await db.execute(
        select(Wishlist).where(Wishlist.user_id == user_id, Wishlist.product_id == product_id)
    )
    existing = r.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        return {"added": False, "product_id": product_id}
    else:
        db.add(Wishlist(user_id=user_id, product_id=product_id))
        return {"added": True, "product_id": product_id}


async def wishlist_product_ids(db: AsyncSession, user_id: int) -> list[int]:
    r = await db.execute(select(Wishlist.product_id).where(Wishlist.user_id == user_id))
    return [row[0] for row in r.all()]
