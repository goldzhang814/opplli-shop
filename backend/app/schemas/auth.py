from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Register ──────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email:         EmailStr
    password:      str  = Field(min_length=8, max_length=128)
    agree_terms:   bool
    language_code: str  = "en"
    verification_token: str

    @field_validator("agree_terms")
    @classmethod
    def must_agree(cls, v: bool) -> bool:
        if not v:
            raise ValueError("You must agree to the terms of service")
        return v

    @field_validator("language_code")
    @classmethod
    def valid_language(cls, v: str) -> str:
        if v not in ("en", "es"):
            return "en"
        return v


# ── Login ─────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


# ── Token response ────────────────────────────────────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    expires_in:   int               # seconds
    is_new_user:  bool = False


# ── Authenticated user (me) ───────────────────────────────────────────────────
class UserOut(BaseModel):
    id:            int
    email:         str
    full_name:     Optional[str]
    avatar_url:    Optional[str]
    language_code: str
    is_guest:      bool
    is_active:     bool

    model_config = {"from_attributes": True}


# ── Profile update ────────────────────────────────────────────────────────────
class UpdateProfileRequest(BaseModel):
    full_name:        Optional[str]   = None
    phone:            Optional[str]   = None
    language_code:    Optional[str]   = None
    current_password: Optional[str]   = None
    new_password:     Optional[str]   = Field(default=None, min_length=8, max_length=128)


# ── Password reset ────────────────────────────────────────────────────────────
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token:        str
    new_password: str = Field(min_length=8, max_length=128)


# ── OAuth callback ────────────────────────────────────────────────────────────
class OAuthCallbackResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    is_new_user:  bool


# ── Guest checkout ────────────────────────────────────────────────────────────
class GuestCheckoutRequest(BaseModel):
    email: EmailStr


class GuestClaimRequest(BaseModel):
    """Guest claims their account after receiving claim email."""
    token:    str
    password: str = Field(min_length=8, max_length=128)


# ── Admin login ───────────────────────────────────────────────────────────────
class AdminLoginRequest(BaseModel):
    email:    EmailStr
    password: str


class AdminOut(BaseModel):
    id:          int
    email:       str
    full_name:   Optional[str]
    role:        str
    is_active:   bool
    permissions: dict

    model_config = {"from_attributes": True}
