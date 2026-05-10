"""
Security utilities — JWT token management and password hashing.

Provides stateless JWT creation/validation and bcrypt password
hashing for the authentication system.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from jose import JWTError, jwt
import bcrypt
from src.core.config import get_settings


# ── Password Hashing ────────────────────────────────────────────────


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    # Bcrypt only supports up to 72 bytes. Truncate automatically.
    password_bytes = plain_password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    password_bytes = plain_password[:72].encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except ValueError:
        return False


# ── JWT Token Management ────────────────────────────────────────────


def create_access_token(
    subject: str,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: The token subject (typically user ID).
        extra_claims: Additional claims to embed in the token.
        expires_delta: Custom expiry duration. Defaults to config value.

    Returns:
        Encoded JWT string.
    """
    settings = get_settings()

    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(UTC)
    expire = now + expires_delta

    to_encode: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": expire,
    }

    if extra_claims:
        to_encode.update(extra_claims)

    return str(jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    ))


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT access token.

    Returns:
        The decoded payload dict if valid, None if invalid/expired.
    """
    settings = get_settings()

    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None
