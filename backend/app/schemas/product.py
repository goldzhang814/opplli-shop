from __future__ import annotations
from typing import Optional, Any
from pydantic import BaseModel, Field


# ── Category ──────────────────────────────────────────────────────────────────
class CategoryOut(BaseModel):
    id:          int
    name:        str
    slug:        str
    description: Optional[str]
    parent_id:   Optional[int]
    sort_order:  int
    is_active:   bool
    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name:        str
    slug:        Optional[str] = None
    description: Optional[str] = None
    parent_id:   Optional[int] = None
    sort_order:  int           = 0
    is_active:   bool          = True


class CategoryUpdate(BaseModel):
    name:        Optional[str]  = None
    slug:        Optional[str]  = None
    description: Optional[str]  = None
    parent_id:   Optional[int]  = None
    sort_order:  Optional[int]  = None
    is_active:   Optional[bool] = None


# ── SKU ───────────────────────────────────────────────────────────────────────
class SkuOut(BaseModel):
    id:                  int
    sku_code:            str
    price:               float
    compare_price:       Optional[float]
    stock:               int
    low_stock_threshold: int
    variant_attrs:       Optional[dict]
    is_active:           bool
    free_shipping:       bool
    weight_grams:        Optional[int]
    model_config = {"from_attributes": True}


class SkuCreate(BaseModel):
    sku_code:            str
    price:               float = Field(gt=0)
    compare_price:       Optional[float] = None
    stock:               int   = 0
    low_stock_threshold: int   = 5
    variant_attrs:       Optional[dict] = None
    is_active:           bool  = True
    free_shipping:       bool  = False
    weight_grams:        Optional[int] = None


class SkuUpdate(BaseModel):
    price:               Optional[float] = None
    compare_price:       Optional[float] = None
    stock:               Optional[int]   = None
    low_stock_threshold: Optional[int]   = None
    variant_attrs:       Optional[dict]  = None
    is_active:           Optional[bool]  = None
    free_shipping:       Optional[bool]  = None
    weight_grams:        Optional[int]   = None


# ── Product image ─────────────────────────────────────────────────────────────
class ProductImageOut(BaseModel):
    id:           int
    url:          str   # resolved public URL
    alt_text:     Optional[str]
    sort_order:   int
    storage_type: str
    model_config = {"from_attributes": True}


# ── Product ───────────────────────────────────────────────────────────────────
class ProductOut(BaseModel):
    id:              int
    name:            str
    slug:            str
    description:     Optional[str]
    short_desc:      Optional[str]
    category_id:     Optional[int]
    category_name:   Optional[str] = None
    is_published:    bool
    rating_avg:      float
    rating_count:    int
    seo_title:       Optional[str]
    seo_description: Optional[str]
    seo_slug:        Optional[str]
    og_image:        Optional[str]
    skus:            list[SkuOut]   = []
    images:          list[ProductImageOut] = []
    model_config = {"from_attributes": True}


class ProductListItem(BaseModel):
    id:           int
    name:         str
    slug:         str
    is_published: bool
    rating_avg:   float
    rating_count: int
    category_id:  Optional[int]
    category_name:Optional[str] = None
    min_price:    Optional[float] = None
    max_price:    Optional[float] = None
    cover_image:  Optional[str]  = None
    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name:            str
    slug:            Optional[str]  = None
    description:     Optional[str]  = None
    short_desc:      Optional[str]  = None
    category_id:     Optional[int]  = None
    is_published:    bool           = False
    seo_title:       Optional[str]  = None
    seo_description: Optional[str]  = None
    seo_slug:        Optional[str]  = None
    og_image:        Optional[str]  = None
    skus:            list[SkuCreate] = []


class ProductUpdate(BaseModel):
    name:            Optional[str]  = None
    slug:            Optional[str]  = None
    description:     Optional[str]  = None
    short_desc:      Optional[str]  = None
    category_id:     Optional[int]  = None
    is_published:    Optional[bool] = None
    seo_title:       Optional[str]  = None
    seo_description: Optional[str]  = None
    seo_slug:        Optional[str]  = None
    og_image:        Optional[str]  = None


class PaginatedProducts(BaseModel):
    items:  list[ProductListItem]
    total:  int
    page:   int
    pages:  int
    limit:  int


# ── Inventory ─────────────────────────────────────────────────────────────────
class InventoryAdjust(BaseModel):
    change_qty: int   # positive = add, negative = remove
    reason:     str   = "manual"
    note:       Optional[str] = None


class InventoryLogOut(BaseModel):
    id:           int
    sku_id:       int
    change_qty:   int
    before_qty:   int
    after_qty:    int
    reason:       str
    reference_id: Optional[str]
    created_at:   Any
    model_config = {"from_attributes": True}


# ── Reviews ───────────────────────────────────────────────────────────────────
class ReviewSubmit(BaseModel):
    product_id:    int
    order_id:      Optional[int] = None
    rating:        int = Field(ge=1, le=5)
    content:       Optional[str] = None
    reviewer_name: Optional[str] = None


class ReviewOut(BaseModel):
    id:                   int
    product_id:           int
    user_id:              int
    rating:               int
    content:              Optional[str]
    status:               str
    reviewer_name:        Optional[str]
    is_verified_purchase: bool
    media:                list[dict] = []
    created_at:           Any
    model_config = {"from_attributes": True}


class ReviewModerate(BaseModel):
    action:        str              # approve | reject
    reject_reason: Optional[str] = None


class PaginatedReviews(BaseModel):
    items:  list[ReviewOut]
    total:  int
    page:   int
    pages:  int


# ── Wishlist ──────────────────────────────────────────────────────────────────
class WishlistItem(BaseModel):
    product_id:   int
    product_name: str
    slug:         str
    cover_image:  Optional[str]
    min_price:    Optional[float]
    model_config = {"from_attributes": True}
