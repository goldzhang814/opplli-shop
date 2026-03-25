"""
FastAPI Dependencies
====================
- get_current_user       → authenticated customer (raises 401 if not)
- get_current_user_opt   → customer OR None (for optional auth endpoints)
- get_current_admin      → authenticated admin (raises 401/403)
- require_permission(mod)→ factory that checks admin module permission
- get_guest_token        → reads X-Guest-Token header
"""
from __future__ import annotations
from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError

from app.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.models.admin import Admin

bearer = HTTPBearer(auto_error=False)


# ── Customer ──────────────────────────────────────────────────────────────────
async def _resolve_user(
    credentials: Optional[HTTPAuthorizationCredentials],
    db: AsyncSession,
) -> Optional[User]:
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        return None
    if not payload.sub.startswith("user:"):
        return None
    user_id = int(payload.sub.split(":")[1])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user and not user.is_active:
        return None
    return user


async def get_current_user_opt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    return await _resolve_user(credentials, db)


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_opt),
) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ── Admin ─────────────────────────────────────────────────────────────────────
async def get_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> Admin:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin authentication required",
    )
    if not credentials:
        raise exc
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise exc
    if not payload.sub.startswith("admin:"):
        raise exc
    admin_id = int(payload.sub.split(":")[1])
    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin or not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin account inactive")
    return admin


def require_permission(module: str):
    """Factory — use as: admin=Depends(require_permission('products'))"""
    async def _check(admin: Admin = Depends(get_current_admin)) -> Admin:
        if admin.role == "super_admin":
            return admin
        if not admin.permissions.get(module):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: module '{module}'",
            )
        return admin
    return _check


# ── Guest token ───────────────────────────────────────────────────────────────
async def get_guest_token(
    x_guest_token: Optional[str] = Header(default=None),
) -> Optional[str]:
    return x_guest_token
