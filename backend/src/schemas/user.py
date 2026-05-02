"""
User-related Pydantic schemas.

Defines request/response models for authentication endpoints
including registration, login, and profile responses.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ── Request Schemas ──────────────────────────────────────────────────


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be at least 8 characters",
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User's full name",
    )


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


# ── Response Schemas ─────────────────────────────────────────────────


class UserResponse(BaseModel):
    """Safe user representation — never includes password."""

    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload."""

    sub: str
    exp: datetime | None = None
