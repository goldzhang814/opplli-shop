"""
Admin Product Router
====================
Categories:
  GET    /api/v1/admin/categories
  POST   /api/v1/admin/categories
  PUT    /api/v1/admin/categories/{id}
  DELETE /api/v1/admin/categories/{id}

Products:
  GET    /api/v1/admin/products
  POST   /api/v1/admin/products
  GET    /api/v1/admin/products/{id}
  PUT    /api/v1/admin/products/{id}
  DELETE /api/v1/admin/products/{id}
  POST   /api/v1/admin/products/{id}/publish
  POST   /api/v1/admin/products/{id}/unpublish

SKUs:
  POST   /api/v1/admin/products/{id}/skus
  PUT    /api/v1/admin/products/{id}/skus/{sku_id}
  DELETE /api/v1/admin/products/{id}/skus/{sku_id}

Images:
  POST   /api/v1/admin/products/{id}/images
  DELETE /api/v1/admin/products/{id}/images/{image_id}
  PUT    /api/v1/admin/products/{id}/images/reorder

Inventory:
  POST   /api/v1/admin/skus/{sku_id}/inventory
  GET    /api/v1/admin/inventory/logs
  GET    /api/v1/admin/inventory/low-stock

Reviews:
  GET    /api/v1/admin/reviews
  POST   /api/v1/admin/reviews/{id}/moderate
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.core.dependencies import require_permission
from app.models.admin import Admin
from app.schemas.product import (
    CategoryOut, CategoryCreate, CategoryUpdate,
    ProductOut, ProductCreate, ProductUpdate, PaginatedProducts,
    SkuCreate, SkuUpdate, SkuOut,
    InventoryAdjust, InventoryLogOut,
    ReviewModerate, PaginatedReviews,
)
from app.services import product_service
from app.core.storage import resolve_url

router = APIRouter(prefix="/admin", tags=["Admin — Products"])


# ── Categories ────────────────────────────────────────────────────────────────
@router.get("/categories", response_model=list[CategoryOut])
async def admin_list_categories(
    _:  Admin        = Depends(require_permission("categories")),
    db: AsyncSession = Depends(get_db),
):
    return await product_service.list_categories(db, active_only=False)


@router.post("/categories", response_model=CategoryOut, status_code=201)
async def admin_create_category(
    req: CategoryCreate,
    _:   Admin        = Depends(require_permission("categories")),
    db:  AsyncSession = Depends(get_db),
):
    return await product_service.create_category(db, req)


@router.put("/categories/{cat_id}", response_model=CategoryOut)
async def admin_update_category(
    cat_id: int,
    req:    CategoryUpdate,
    _:      Admin        = Depends(require_permission("categories")),
    db:     AsyncSession = Depends(get_db),
):
    return await product_service.update_category(db, cat_id, req)


@router.delete("/categories/{cat_id}", status_code=204)
async def admin_delete_category(
    cat_id: int,
    _:      Admin        = Depends(require_permission("categories")),
    db:     AsyncSession = Depends(get_db),
):
    await product_service.delete_category(db, cat_id)


# ── Products ──────────────────────────────────────────────────────────────────
@router.get("/products", response_model=PaginatedProducts)
async def admin_list_products(
    page:        int           = Query(1, ge=1),
    limit:       int           = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    search:      Optional[str] = None,
    sort:        str           = "created_desc",
    _:           Admin         = Depends(require_permission("products")),
    db:          AsyncSession  = Depends(get_db),
):
    return await product_service.list_products(
        db, page=page, limit=limit,
        category_id=category_id, search=search,
        published_only=False, sort=sort,
    )


@router.post("/products", response_model=ProductOut, status_code=201)
async def admin_create_product(
    req: ProductCreate,
    _:   Admin        = Depends(require_permission("products")),
    db:  AsyncSession = Depends(get_db),
):
    return await product_service.create_product(db, req)


@router.get("/products/{product_id}", response_model=ProductOut)
async def admin_get_product(
    product_id: int,
    _:          Admin        = Depends(require_permission("products")),
    db:         AsyncSession = Depends(get_db),
):
    p      = await product_service.get_product_by_id(db, product_id)
    result = ProductOut.model_validate(p)
    result.images       = product_service._resolve_images(p.images)  # type: ignore
    result.category_name = p.category.name if p.category else None
    return result


@router.put("/products/{product_id}", response_model=ProductOut)
async def admin_update_product(
    product_id: int,
    req:        ProductUpdate,
    _:          Admin        = Depends(require_permission("products")),
    db:         AsyncSession = Depends(get_db),
):
    return await product_service.update_product(db, product_id, req)


@router.delete("/products/{product_id}", status_code=204)
async def admin_delete_product(
    product_id: int,
    _:          Admin        = Depends(require_permission("products")),
    db:         AsyncSession = Depends(get_db),
):
    await product_service.delete_product(db, product_id)


@router.post("/products/{product_id}/publish")
async def admin_publish(
    product_id: int,
    _:          Admin        = Depends(require_permission("products")),
    db:         AsyncSession = Depends(get_db),
):
    p = await product_service.publish_product(db, product_id, True)
    return {"id": p.id, "is_published": p.is_published}


@router.post("/products/{product_id}/unpublish")
async def admin_unpublish(
    product_id: int,
    _:          Admin        = Depends(require_permission("products")),
    db:         AsyncSession = Depends(get_db),
):
    p = await product_service.publish_product(db, product_id, False)
    return {"id": p.id, "is_published": p.is_published}


# ── SKUs ──────────────────────────────────────────────────────────────────────
@router.post("/products/{product_id}/skus", response_model=SkuOut, status_code=201)
async def admin_create_sku(
    product_id: int,
    req:        SkuCreate,
    _:          Admin        = Depends(require_permission("products")),
    db:         AsyncSession = Depends(get_db),
):
    return await product_service.create_sku(db, product_id, req)


@router.put("/products/{product_id}/skus/{sku_id}", response_model=SkuOut)
async def admin_update_sku(
    product_id: int,
    sku_id:     int,
    req:        SkuUpdate,
    _:          Admin        = Depends(require_permission("products")),
    db:         AsyncSession = Depends(get_db),
):
    return await product_service.update_sku(db, sku_id, req)


@router.delete("/products/{product_id}/skus/{sku_id}", status_code=204)
async def admin_delete_sku(
    product_id: int,
    sku_id:     int,
    _:          Admin        = Depends(require_permission("products")),
    db:         AsyncSession = Depends(get_db),
):
    await product_service.delete_sku(db, sku_id)


# ── Images ────────────────────────────────────────────────────────────────────
@router.post("/products/{product_id}/images", status_code=201)
async def admin_upload_image(
    product_id: int,
    file:       UploadFile    = File(...),
    alt_text:   Optional[str] = Form(None),
    _:          Admin         = Depends(require_permission("products")),
    db:         AsyncSession  = Depends(get_db),
):
    img = await product_service.upload_product_image(db, product_id, file, alt_text)
    return {
        "id":  img.id,
        "url": resolve_url(img.url, img.storage_type),
        "storage_type": img.storage_type,
    }


@router.delete("/products/{product_id}/images/{image_id}", status_code=204)
async def admin_delete_image(
    product_id: int,
    image_id:   int,
    _:          Admin        = Depends(require_permission("products")),
    db:         AsyncSession = Depends(get_db),
):
    await product_service.delete_product_image(db, image_id)


class ReorderRequest(BaseModel):
    ordered_ids: list[int]


@router.put("/products/{product_id}/images/reorder", status_code=204)
async def admin_reorder_images(
    product_id: int,
    req:        ReorderRequest,
    _:          Admin        = Depends(require_permission("products")),
    db:         AsyncSession = Depends(get_db),
):
    await product_service.reorder_images(db, product_id, req.ordered_ids)


# ── Inventory ─────────────────────────────────────────────────────────────────
@router.post("/skus/{sku_id}/inventory")
async def admin_adjust_inventory(
    sku_id: int,
    req:    InventoryAdjust,
    admin:  Admin        = Depends(require_permission("inventory")),
    db:     AsyncSession = Depends(get_db),
):
    sku = await product_service.adjust_inventory(db, sku_id, req, operator_id=admin.id)
    return {"sku_id": sku.id, "new_stock": sku.stock}


@router.get("/inventory/logs")
async def admin_inventory_logs(
    sku_id: Optional[int] = None,
    page:   int           = Query(1, ge=1),
    _:      Admin         = Depends(require_permission("inventory")),
    db:     AsyncSession  = Depends(get_db),
):
    return await product_service.get_inventory_logs(db, sku_id=sku_id, page=page)


@router.get("/inventory/low-stock")
async def admin_low_stock(
    _:  Admin        = Depends(require_permission("inventory")),
    db: AsyncSession = Depends(get_db),
):
    skus = await product_service.get_low_stock_skus(db)
    return [
        {
            "sku_id":       s.id,
            "sku_code":     s.sku_code,
            "stock":        s.stock,
            "threshold":    s.low_stock_threshold,
            "product_id":   s.product_id,
            "product_name": s.product.name if s.product else None,
        }
        for s in skus
    ]


# ── Reviews ───────────────────────────────────────────────────────────────────
@router.get("/reviews", response_model=PaginatedReviews)
async def admin_list_reviews(
    product_id:    Optional[int] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page:          int           = Query(1, ge=1),
    _:             Admin         = Depends(require_permission("reviews")),
    db:            AsyncSession  = Depends(get_db),
):
    return await product_service.list_reviews(
        db, product_id=product_id, status_filter=status_filter, page=page
    )


@router.post("/reviews/{review_id}/moderate")
async def admin_moderate_review(
    review_id: int,
    req:       ReviewModerate,
    _:         Admin        = Depends(require_permission("reviews")),
    db:        AsyncSession = Depends(get_db),
):
    review = await product_service.moderate_review(db, review_id, req)
    return {"id": review.id, "status": review.status}
