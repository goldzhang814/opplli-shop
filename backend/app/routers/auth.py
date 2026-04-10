"""
Customer Auth Router
====================
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/guest
POST /api/v1/auth/guest/claim
GET  /api/v1/auth/me
PUT  /api/v1/auth/me
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
GET  /api/v1/auth/google
GET  /api/v1/auth/google/callback
GET  /api/v1/auth/facebook
GET  /api/v1/auth/facebook/callback
GET  /api/v1/auth/facebook/webhook
POST /api/v1/auth/apple/callback
"""
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, UserOut,
    UpdateProfileRequest, ForgotPasswordRequest, ResetPasswordRequest,
    GuestCheckoutRequest, GuestClaimRequest,
)
from app.services import auth_service
from app.config import settings
from app.services import verification_service
from pydantic import BaseModel as _BM, EmailStr as _Email

class SendCodeRequest(_BM):
    email: _Email

class VerifyCodeRequest(_BM):
    email:   _Email
    code:    str

def _safe_redirect_path(raw: Optional[str]) -> str:
    if not raw:
        return "/"
    if raw.startswith(("http://", "https://", "//")):
        return "/"
    if not raw.startswith("/"):
        return "/"
    return raw

router = APIRouter(prefix="/auth", tags=["Auth"])

VERIFY_TOKEN = "opplii_fb_verify_token_9xK3LmP2"

# ── Register ──────────────────────────────────────────────────────────────────
@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # 验证 token（同时获取 email，防止前端篡改 email）
    verified_email = verification_service.consume_verification_token(req.verification_token)
    if verified_email != req.email:
        return Response(content="Email mismatch. Please re-verify.",status_code=status.HTTP_400_BAD_REQUEST)
    return await auth_service.register(db, req)


# ── Login ─────────────────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, req)


# ── Me ────────────────────────────────────────────────────────────────────────
@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=UserOut)
async def update_me(
    req:  UpdateProfileRequest,
    user: User             = Depends(get_current_user),
    db:   AsyncSession     = Depends(get_db),
):
    return await auth_service.update_profile(db, user, req)


@router.post("/delete-account", status_code=204)
async def delete_account(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.anonymize_user(db, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── Guest checkout ────────────────────────────────────────────────────────────
@router.post("/guest", response_model=TokenResponse, status_code=201)
async def guest_checkout(req: GuestCheckoutRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.get_or_create_guest(db, req)


@router.post("/guest/claim", response_model=TokenResponse)
async def claim_guest(req: GuestClaimRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.claim_guest_account(db, req)


# ── Forgot / Reset password ───────────────────────────────────────────────────
@router.post("/forgot-password", status_code=204)
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    await auth_service.forgot_password(db, req)


@router.post("/reset-password", status_code=204)
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await auth_service.reset_password(db, req)


# ── Google OAuth ──────────────────────────────────────────────────────────────
@router.get("/google")
async def google_login(redirect: Optional[str] = None):
    params = {
        "client_id":     settings.GOOGLE_CLIENT_ID,
        "redirect_uri":  settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
    }
    safe_redirect = _safe_redirect_path(redirect)
    if safe_redirect != "/":
        params["state"] = safe_redirect
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    )


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    res = await auth_service.google_callback(db, code)
    safe_redirect = _safe_redirect_path(state)
    fragment = urlencode(
        {
            "token": res["access_token"],
            "is_new": str(res.get("is_new_user", False)).lower(),
            "redirect": safe_redirect,
        }
    )
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/oauth#{fragment}")


# ── Facebook OAuth ────────────────────────────────────────────────────────────
@router.get("/facebook")
async def facebook_login(redirect: Optional[str] = None):
    params = {
        "client_id":     settings.FACEBOOK_CLIENT_ID,
        "redirect_uri":  settings.FACEBOOK_REDIRECT_URI,
        "scope":         "email,public_profile",
    }
    safe_redirect = _safe_redirect_path(redirect)
    if safe_redirect != "/":
        params["state"] = safe_redirect
    return RedirectResponse(
        f"https://www.facebook.com/v19.0/dialog/oauth?{urlencode(params)}"
    )


@router.get("/facebook/callback")
async def facebook_callback(
    code: str,
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    res = await auth_service.facebook_callback(db, code)
    safe_redirect = _safe_redirect_path(state)
    fragment = urlencode(
        {
            "token": res["access_token"],
            "is_new": str(res.get("is_new_user", False)).lower(),
            "redirect": safe_redirect,
        }
    )
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/oauth#{fragment}")

@router.get("/facebook/webhook")
async def facebook_webhook_verify(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")

    return Response(content="Forbidden", status_code=403)


# ── Apple OAuth ───────────────────────────────────────────────────────────────
@router.post("/apple/callback")
async def apple_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    form = await request.form()
    code     = form.get("code", "")
    id_token = form.get("id_token", "")
    user_str = form.get("user")
    state = form.get("state")
    res = await auth_service.apple_callback(db, code, id_token, user_str)
    safe_redirect = _safe_redirect_path(state)
    fragment = urlencode(
        {
            "token": res["access_token"],
            "is_new": str(res.get("is_new_user", False)).lower(),
            "redirect": safe_redirect,
        }
    )
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/oauth#{fragment}")


# ── User Addresses ────────────────────────────────────────────────────────────
from pydantic import BaseModel as _BaseModel
from app.models.user import UserAddress
from sqlalchemy import select as _select

class AddressIn(_BaseModel):
    full_name:     str
    phone:         Optional[str]  = None
    country_code:  str
    state_code:    Optional[str]  = None
    state_name:    Optional[str]  = None
    city:          str
    address_line1: str
    address_line2: Optional[str]  = None
    postal_code:   str
    is_default:    bool           = False


@router.get("/addresses")
async def list_addresses(
    user: User         = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    r = await db.execute(
        _select(UserAddress)
        .where(UserAddress.user_id == user.id)
        .order_by(UserAddress.is_default.desc(), UserAddress.id.desc())
    )
    addrs = r.scalars().all()
    return [
        {
            "id":           a.id,
            "full_name":    a.full_name,
            "phone":        a.phone,
            "country_code": a.country_code,
            "state_code":   a.state_code,
            "state_name":   a.state_name,
            "city":         a.city,
            "address_line1":a.address_line1,
            "address_line2":a.address_line2,
            "postal_code":  a.postal_code,
            "is_default":   a.is_default,
        }
        for a in addrs
    ]


@router.post("/addresses", status_code=201)
async def create_address(
    req:  AddressIn,
    user: User         = Depends(get_current_user),
    db:   AsyncSession = Depends(get_db),
):
    # If new address is default, unset others
    if req.is_default:
        from sqlalchemy import update as _update
        await db.execute(
            _update(UserAddress)
            .where(UserAddress.user_id == user.id)
            .values(is_default=False)
        )
    addr = UserAddress(user_id=user.id, **req.model_dump())
    db.add(addr)
    await db.flush()
    return {"id": addr.id, "message": "Address saved"}


@router.put("/addresses/{addr_id}")
async def update_address(
    addr_id: int,
    req:     AddressIn,
    user:    User         = Depends(get_current_user),
    db:      AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException as _HTTPException
    r    = await db.execute(
        _select(UserAddress).where(UserAddress.id == addr_id, UserAddress.user_id == user.id)
    )
    addr = r.scalar_one_or_none()
    if not addr:
        raise _HTTPException(404, "Address not found")
    if req.is_default:
        from sqlalchemy import update as _update
        await db.execute(
            _update(UserAddress)
            .where(UserAddress.user_id == user.id, UserAddress.id != addr_id)
            .values(is_default=False)
        )
    for k, v in req.model_dump().items():
        setattr(addr, k, v)
    return {"id": addr.id, "message": "Address updated"}


@router.delete("/addresses/{addr_id}", status_code=204)
async def delete_address(
    addr_id: int,
    user:    User         = Depends(get_current_user),
    db:      AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException as _HTTPException
    r    = await db.execute(
        _select(UserAddress).where(UserAddress.id == addr_id, UserAddress.user_id == user.id)
    )
    addr = r.scalar_one_or_none()
    if not addr:
        raise _HTTPException(404, "Address not found")
    await db.delete(addr)


@router.post("/addresses/{addr_id}/set-default")
async def set_default_address(
    addr_id: int,
    user:    User         = Depends(get_current_user),
    db:      AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException as _HTTPException
    from sqlalchemy import update as _update
    r    = await db.execute(
        _select(UserAddress).where(UserAddress.id == addr_id, UserAddress.user_id == user.id)
    )
    addr = r.scalar_one_or_none()
    if not addr:
        raise _HTTPException(404, "Address not found")
    await db.execute(
        _update(UserAddress)
        .where(UserAddress.user_id == user.id)
        .values(is_default=False)
    )
    addr.is_default = True
    return {"message": "Default address updated"}

@router.post("/send-verification")
async def send_verification(
    req: SendCodeRequest,
    db:  AsyncSession = Depends(get_db),
):
    await verification_service.send_verification_code(db, req.email, purpose='register')
    return {"message": "Verification code sent"}


@router.post("/verify-code")
async def verify_code(
    req: VerifyCodeRequest,
    db:  AsyncSession = Depends(get_db),
):
    token = await verification_service.verify_code(db, req.email, req.code, purpose='register')
    return {"verification_token": token}