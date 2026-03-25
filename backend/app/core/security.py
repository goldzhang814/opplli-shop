"""
Security utilities
==================
- Password hashing via bcrypt (SHA-256 pre-hash for passwords > 72 bytes)
- JWT access token creation / verification
- Token payload models
"""
from __future__ import annotations
import hashlib
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel
from app.config import settings


# ── Password ──────────────────────────────────────────────────────────────────
def _normalise(plain: str) -> bytes:
    """SHA-256 pre-hash so passwords > 72 bytes are handled safely."""
    raw = plain.encode("utf-8")
    if len(raw) > 72:
        raw = hashlib.sha256(raw).hexdigest().encode("utf-8")
    return raw


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(_normalise(plain), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_normalise(plain), hashed.encode("utf-8"))
    except Exception:
        return False


# ── JWT ───────────────────────────────────────────────────────────────────────
class TokenPayload(BaseModel):
    sub:  str             # "user:{id}" or "admin:{id}"
    role: str             # customer | admin | super_admin
    exp:  Optional[int] = None


def create_access_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + delta
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """Raises JWTError on invalid/expired token."""
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return TokenPayload(**payload)
