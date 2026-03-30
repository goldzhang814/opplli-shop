"""
Admin Users Router
==================
GET /api/v1/admin/users
"""
import math
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.dependencies import require_permission
from app.models.admin import Admin
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin - Users"])


@router.get("/users")
async def admin_list_users(
    page:   int           = Query(1, ge=1),
    limit:  int           = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    _:      Admin         = Depends(require_permission("orders")),
    db:     AsyncSession  = Depends(get_db),
):
    q = select(User).where(User.is_guest == False, User.role == "customer")
    if search:
        like = f"%{search}%"
        q = q.where(or_(User.email.ilike(like), User.full_name.ilike(like)))
    q = q.order_by(User.created_at.desc())

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset((page - 1) * limit).limit(limit))).scalars().all()

    return {
        "items": [
            {
                "id":         u.id,
                "email":      u.email,
                "full_name":  u.full_name,
                "phone":      u.phone,
                "language_code":  u.language_code,
                "is_active":  u.is_active,
                "created_at": u.created_at,
            }
            for u in items
        ],
        "total": total,
        "page":  page,
        "pages": max(1, math.ceil(total / limit)),
    }
