"""
Auth Service
============
Handles: register, login, OAuth, guest checkout, password reset,
         guest-to-real-account claim, profile update.
"""
from __future__ import annotations
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, OAuthAccount, PasswordResetToken, GuestClaimToken
from app.schemas.auth import (
    RegisterRequest, LoginRequest, UpdateProfileRequest,
    GuestCheckoutRequest, GuestClaimRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _token_response(user: User, is_new: bool = False) -> dict:
    expires = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    token   = create_access_token(f"user:{user.id}", user.role)
    return {"access_token": token, "token_type": "bearer",
            "expires_in": expires, "is_new_user": is_new}


async def _get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    r = await db.execute(select(User).where(User.email == email))
    return r.scalar_one_or_none()


# ── Register ──────────────────────────────────────────────────────────────────
async def register(db: AsyncSession, req: RegisterRequest) -> dict:
    existing = await _get_user_by_email(db, req.email)
    if existing:
        if existing.is_guest:
            existing.password_hash = hash_password(req.password)
            existing.is_guest      = False
            existing.is_active     = True
            existing.agree_terms   = True
            existing.agreed_at     = datetime.now(timezone.utc)
            existing.language_code = req.language_code
            return _token_response(existing, is_new=False)
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    user = User(
        email         = req.email,
        password_hash = hash_password(req.password),
        language_code = req.language_code,
        agree_terms   = True,
        agreed_at     = datetime.now(timezone.utc),
        is_guest      = False,
        is_active     = True,
        role          = "customer",
    )
    db.add(user)
    await db.flush()
    return _token_response(user, is_new=True)


# ── Login ─────────────────────────────────────────────────────────────────────
async def login(db: AsyncSession, req: LoginRequest) -> dict:
    user = await _get_user_by_email(db, req.email)
    if not user or not user.password_hash:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is disabled")
    return _token_response(user)


# ── Guest checkout ────────────────────────────────────────────────────────────
async def get_or_create_guest(db: AsyncSession, req: GuestCheckoutRequest) -> dict:
    """
    Returns a JWT for the guest user (creates if not exists).
    Frontend stores this token and sends it as X-Guest-Token header.
    """
    user = await _get_user_by_email(db, req.email)
    if user and not user.is_guest:
        # Real user already exists — let them know to log in
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "An account with this email exists. Please sign in.",
        )
    if not user:
        user = User(
            email      = req.email,
            is_guest   = True,
            is_active  = True,
            role       = "customer",
            agree_terms= False,
        )
        db.add(user)
        await db.flush()
    return _token_response(user, is_new=True)


# ── Guest claim ───────────────────────────────────────────────────────────────
async def claim_guest_account(db: AsyncSession, req: GuestClaimRequest) -> dict:
    r = await db.execute(
        select(GuestClaimToken).where(
            GuestClaimToken.token == req.token,
            GuestClaimToken.used  == False,
        )
    )
    claim = r.scalar_one_or_none()
    if not claim:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired claim token")
    if claim.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Claim token has expired")

    r2   = await db.execute(select(User).where(User.id == claim.user_id))
    user = r2.scalar_one_or_none()
    if not user or not user.is_guest:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid claim token")

    user.password_hash = hash_password(req.password)
    user.is_guest      = False
    user.agree_terms   = True
    user.agreed_at     = datetime.now(timezone.utc)
    claim.used         = True
    return _token_response(user)


# ── OAuth: Google ─────────────────────────────────────────────────────────────
async def google_callback(db: AsyncSession, code: str) -> dict:
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code":          code,
                "client_id":     settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri":  settings.GOOGLE_REDIRECT_URI,
                "grant_type":    "authorization_code",
            },
        )
        token_res.raise_for_status()
        tokens = token_res.json()

        # Get user info
        info_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        info_res.raise_for_status()
        info = info_res.json()

    return await _oauth_upsert(
        db,
        provider         = "google",
        provider_user_id = info["id"],
        email            = info.get("email", ""),
        full_name        = info.get("name"),
        avatar_url       = info.get("picture"),
        access_token     = tokens.get("access_token"),
        refresh_token    = tokens.get("refresh_token"),
    )


# ── OAuth: Facebook ───────────────────────────────────────────────────────────
async def facebook_callback(db: AsyncSession, code: str) -> dict:
    async with httpx.AsyncClient() as client:
        token_res = await client.get(
            "https://graph.facebook.com/v19.0/oauth/access_token",
            params={
                "client_id":     settings.FACEBOOK_CLIENT_ID,
                "client_secret": settings.FACEBOOK_CLIENT_SECRET,
                "redirect_uri":  settings.FACEBOOK_REDIRECT_URI,
                "code":          code,
            },
        )
        token_res.raise_for_status()
        tokens = token_res.json()

        info_res = await client.get(
            "https://graph.facebook.com/me",
            params={"fields": "id,name,email,picture", "access_token": tokens["access_token"]},
        )
        info_res.raise_for_status()
        info = info_res.json()

    return await _oauth_upsert(
        db,
        provider         = "facebook",
        provider_user_id = info["id"],
        email            = info.get("email", f"fb_{info['id']}@noemail.local"),
        full_name        = info.get("name"),
        avatar_url       = info.get("picture", {}).get("data", {}).get("url"),
        access_token     = tokens.get("access_token"),
    )


# ── OAuth: Apple ──────────────────────────────────────────────────────────────
async def apple_callback(db: AsyncSession, code: str, id_token: str, user_json: Optional[str] = None) -> dict:
    """
    Apple sends id_token as JWT. We decode it to get sub (unique user id) and email.
    user_json is only sent on first login and contains name.
    """
    import json
    from jose import jwt as jose_jwt

    # Decode Apple id_token (don't verify sig here — use Apple's public keys in production)
    claims = jose_jwt.get_unverified_claims(id_token)
    apple_sub = claims.get("sub", "")
    email     = claims.get("email", f"apple_{apple_sub}@privaterelay.appleid.com")

    full_name = None
    if user_json:
        try:
            user_data = json.loads(user_json)
            name      = user_data.get("name", {})
            full_name = f"{name.get('firstName', '')} {name.get('lastName', '')}".strip() or None
        except Exception:
            pass

    return await _oauth_upsert(
        db,
        provider         = "apple",
        provider_user_id = apple_sub,
        email            = email,
        full_name        = full_name,
    )


# ── OAuth shared upsert ───────────────────────────────────────────────────────
async def _oauth_upsert(
    db: AsyncSession,
    *,
    provider: str,
    provider_user_id: str,
    email: str,
    full_name: Optional[str]  = None,
    avatar_url: Optional[str] = None,
    access_token: Optional[str]  = None,
    refresh_token: Optional[str] = None,
) -> dict:
    # 1. Check if OAuth account already exists
    r = await db.execute(
        select(OAuthAccount).where(
            OAuthAccount.provider         == provider,
            OAuthAccount.provider_user_id == provider_user_id,
        )
    )
    oauth_acc = r.scalar_one_or_none()

    if oauth_acc:
        # Update tokens
        oauth_acc.access_token  = access_token
        oauth_acc.refresh_token = refresh_token
        r2   = await db.execute(select(User).where(User.id == oauth_acc.user_id))
        user = r2.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")
        return _token_response(user, is_new=False)

    # 2. Try to find user by email (auto-link)
    user = await _get_user_by_email(db, email)
    is_new = False

    if not user:
        # Create new user
        user = User(
            email         = email,
            full_name     = full_name,
            avatar_url    = avatar_url,
            language_code = "en",
            is_guest      = False,
            is_active     = True,
            agree_terms   = True,
            agreed_at     = datetime.now(timezone.utc),
            role          = "customer",
        )
        db.add(user)
        await db.flush()
        is_new = True
    elif user.is_guest:
        # Upgrade guest to real account
        user.is_guest   = False
        user.agree_terms= True
        user.agreed_at  = datetime.now(timezone.utc)
        if full_name and not user.full_name:
            user.full_name = full_name

    # 3. Create OAuth account record
    new_oauth = OAuthAccount(
        user_id          = user.id,
        provider         = provider,
        provider_user_id = provider_user_id,
        access_token     = access_token,
        refresh_token    = refresh_token,
    )
    db.add(new_oauth)
    return _token_response(user, is_new=is_new)


# ── Forgot / Reset password ───────────────────────────────────────────────────
async def forgot_password(db: AsyncSession, req: ForgotPasswordRequest) -> None:
    """
    Always returns 200 (don't leak whether email exists).
    Queues email via Celery.
    """
    user = await _get_user_by_email(db, req.email)
    if not user or user.is_guest:
        return  # silent

    token    = secrets.token_urlsafe(48)
    expires  = datetime.now(timezone.utc) + timedelta(hours=1)
    pw_token = PasswordResetToken(user_id=user.id, token=token, expires_at=expires)
    db.add(pw_token)
    await db.flush()

    # Queue email task
    from app.tasks.email_tasks import send_password_reset_email
    send_password_reset_email.delay(
        user_id  = user.id,
        email    = user.email,
        token    = token,
        language = user.language_code,
    )


async def reset_password(db: AsyncSession, req: ResetPasswordRequest) -> None:
    r = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == req.token,
            PasswordResetToken.used  == False,
        )
    )
    pw_token = r.scalar_one_or_none()
    if not pw_token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired reset token")
    if pw_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Reset token has expired")

    r2   = await db.execute(select(User).where(User.id == pw_token.user_id))
    user = r2.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User not found")

    user.password_hash = hash_password(req.new_password)
    pw_token.used      = True


# ── Update profile ────────────────────────────────────────────────────────────
async def update_profile(db: AsyncSession, user: User, req: UpdateProfileRequest) -> User:
    if req.full_name     is not None: user.full_name     = req.full_name
    if req.phone         is not None: user.phone         = req.phone
    if req.language_code is not None:
        if req.language_code in ("en", "es"):
            user.language_code = req.language_code

    if req.new_password:
        if not req.current_password:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                "current_password required to set new password")
        if not user.password_hash or not verify_password(req.current_password, user.password_hash):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
        user.password_hash = hash_password(req.new_password)

    return user
