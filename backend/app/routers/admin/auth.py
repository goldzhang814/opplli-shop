"""
Admin Auth Router
=================
POST /api/v1/admin/login
GET  /api/v1/admin/me
GET  /api/v1/admin/admins
POST /api/v1/admin/admins
PUT  /api/v1/admin/admins/{id}/permissions
PUT  /api/v1/admin/admins/{id}/status
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.core.dependencies import get_current_admin, require_permission
from app.core.security import hash_password, verify_password, create_access_token
from app.models.admin import Admin, SUPER_ADMIN_PERMISSIONS, DEFAULT_PERMISSIONS
from app.schemas.auth import AdminLoginRequest, AdminOut, TokenResponse
from app.config import settings

router = APIRouter(prefix="/admin", tags=["Admin — Auth"])


# ── Login ─────────────────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def admin_login(req: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    r     = await db.execute(select(Admin).where(Admin.email == req.email))
    admin = r.scalar_one_or_none()
    if not admin or not verify_password(req.password, admin.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not admin.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin account disabled")

    admin.last_login_at = datetime.now(timezone.utc)
    token = create_access_token(f"admin:{admin.id}", admin.role)
    expires = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    return {"access_token": token, "token_type": "bearer", "expires_in": expires}


# ── Me ────────────────────────────────────────────────────────────────────────
@router.get("/me", response_model=AdminOut)
async def admin_me(admin: Admin = Depends(get_current_admin)):
    return admin


# ── Admin management ──────────────────────────────────────────────────────────
class CreateAdminRequest(BaseModel):
    email:     EmailStr
    password:  str
    full_name: Optional[str] = None
    role:      str           = "admin"


class UpdatePermissionsRequest(BaseModel):
    permissions: dict[str, bool]


@router.get("/admins", response_model=list[AdminOut])
async def list_admins(
    admin: Admin = Depends(require_permission("admins")),
    db:    AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Admin).order_by(Admin.id))
    return r.scalars().all()


@router.post("/admins", response_model=AdminOut, status_code=201)
async def create_admin(
    req:   CreateAdminRequest,
    admin: Admin       = Depends(require_permission("admins")),
    db:    AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Admin).where(Admin.email == req.email))
    if r.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already used")

    new_admin = Admin(
        email         = req.email,
        password_hash = hash_password(req.password),
        full_name     = req.full_name,
        role          = req.role if admin.role == "super_admin" else "admin",
        is_active     = True,
        permissions   = SUPER_ADMIN_PERMISSIONS if req.role == "super_admin" else dict(DEFAULT_PERMISSIONS),
    )
    db.add(new_admin)
    await db.flush()
    return new_admin


@router.put("/admins/{admin_id}/permissions", response_model=AdminOut)
async def update_permissions(
    admin_id: int,
    req:      UpdatePermissionsRequest,
    caller:   Admin       = Depends(require_permission("admins")),
    db:       AsyncSession = Depends(get_db),
):
    r     = await db.execute(select(Admin).where(Admin.id == admin_id))
    target = r.scalar_one_or_none()
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Admin not found")
    if target.role == "super_admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot modify super admin permissions")
    target.permissions = req.permissions
    return target


@router.put("/admins/{admin_id}/status")
async def toggle_admin_status(
    admin_id: int,
    caller:   Admin       = Depends(require_permission("admins")),
    db:       AsyncSession = Depends(get_db),
):
    r     = await db.execute(select(Admin).where(Admin.id == admin_id))
    target = r.scalar_one_or_none()
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Admin not found")
    if target.role == "super_admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot disable super admin")
    if target.id == caller.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot disable yourself")
    target.is_active = not target.is_active
    return {"id": target.id, "is_active": target.is_active}
