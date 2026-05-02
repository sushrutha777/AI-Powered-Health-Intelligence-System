"""
Authentication service — business logic for user registration and login.

Orchestrates password hashing, user creation, credential verification,
and JWT token generation.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.core.security import create_access_token, hash_password, verify_password
from src.models.user import User
from src.schemas.user import Token, UserCreate, UserResponse

logger = get_logger(__name__)


class AuthService:
    """Handles user authentication and registration logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user.

        Validates email uniqueness, hashes the password, creates the
        user record, and returns the safe user representation.

        Raises:
            ValueError: If email is already registered.
        """
        # Check for existing user
        existing = await self._get_user_by_email(user_data.email)
        if existing:
            logger.warning("registration_duplicate_email", email=user_data.email)
            raise ValueError(f"Email {user_data.email} is already registered")

        # Create new user
        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        logger.info("user_registered", user_id=str(user.id), email=user.email)

        return UserResponse.model_validate(user)

    async def authenticate_user(self, email: str, password: str) -> Token:
        """
        Authenticate a user and return a JWT token.

        Verifies the email exists and password matches, then generates
        a signed access token.

        Raises:
            ValueError: If credentials are invalid.
        """
        user = await self._get_user_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            logger.warning("login_failed", email=email)
            raise ValueError("Invalid email or password")

        if not user.is_active:
            logger.warning("login_inactive_user", email=email)
            raise ValueError("User account is deactivated")

        access_token = create_access_token(subject=str(user.id))

        logger.info("user_logged_in", user_id=str(user.id))

        return Token(access_token=access_token)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Fetch a user by their UUID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_user_by_email(self, email: str) -> User | None:
        """Fetch a user by their email address."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
