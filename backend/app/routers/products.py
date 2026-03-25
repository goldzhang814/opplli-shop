"""
Public Product Router
=====================
GET  /api/v1/products
GET  /api/v1/products/{slug}
GET  /api/v1/products/{slug}/reviews
POST /api/v1/products/{product_id}/reviews    (requires auth)
GET  /api/v1/categories
GET  /api/v1/wishlist                         (requires auth)
POST /api/v1/wishlist/{product_id}            (requires auth)
GET  /api/v1/wishlist/ids                     (requires auth)
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.dependencies import get_current_user, get_current_user_opt
from app.models.user import User
from app.schemas.product import (
    PaginatedProducts, ProductOut, ReviewSubmit,
    PaginatedReviews, CategoryOut, WishlistItem,
)
from app.services import product_service
from app.core.storage import resolve_url

router = APIRouter(tags=["Products"])


# ── Categories ────────────────────────────────────────────────────────────────
@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    return await product_service.list_categories(db, active_only=True)


# ── Products ──────────────────────────────────────────────────────────────────
@router.get("/products", response_model=PaginatedProducts)
async def list_products(
    page:        int           = Query(1, ge=1),
    limit:       int           = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    search:      Optional[str] = None,
    sort:        str           = Query("created_desc", pattern="^(created_desc|created_asc|name_asc|rating_desc)$"),
    db:          AsyncSession  = Depends(get_db),
):
    return await product_service.list_products(
        db, page=page, limit=limit,
        category_id=category_id, search=search,
        published_only=True, sort=sort,
    )


@router.get("/products/{slug}", response_model=ProductOut)
async def get_product(slug: str, db: AsyncSession = Depends(get_db)):
    p      = await product_service.get_product_by_slug(db, slug, published_only=True)
    result = ProductOut.model_validate(p)
    # Resolve image URLs
    result.images = product_service._resolve_images(p.images)  # type: ignore
    if p.category:
        result.category_name = p.category.name
    return result


# ── Reviews ───────────────────────────────────────────────────────────────────
@router.get("/products/{product_id}/reviews", response_model=PaginatedReviews)
async def list_product_reviews(
    product_id: int,
    page:       int          = Query(1, ge=1),
    db:         AsyncSession = Depends(get_db),
):
    return await product_service.list_reviews(
        db, product_id=product_id, status_filter="approved", page=page
    )


@router.post("/products/{product_id}/reviews", status_code=201)
async def submit_review(
    product_id:    int,
    rating:        int           = Form(..., ge=1, le=5),
    content:       Optional[str] = Form(None),
    reviewer_name: Optional[str] = Form(None),
    order_id:      Optional[int] = Form(None),
    media:         list[UploadFile] = File(default=[]),
    user:          User          = Depends(get_current_user),
    db:            AsyncSession  = Depends(get_db),
):
    req = ReviewSubmit(
        product_id    = product_id,
        order_id      = order_id,
        rating        = rating,
        content       = content,
        reviewer_name = reviewer_name,
    )
    review = await product_service.submit_review(db, user.id, req, media_files=media)
    return {"id": review.id, "status": review.status}


# ── Wishlist ──────────────────────────────────────────────────────────────────
@router.get("/wishlist", response_model=list[WishlistItem])
async def get_wishlist(
    user: User         = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    return await product_service.get_wishlist(db, user.id)


@router.post("/wishlist/{product_id}")
async def toggle_wishlist(
    product_id: int,
    user:       User         = Depends(get_current_user),
    db:         AsyncSession = Depends(get_db),
):
    return await product_service.toggle_wishlist(db, user.id, product_id)


@router.get("/wishlist/ids")
async def wishlist_ids(
    user: User         = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    return await product_service.wishlist_product_ids(db, user.id)
