"""
Chat ORM models — ChatSession and ChatMessage.

Stores conversation history for the RAG medical chatbot,
including message content, role, and source citations.
"""

import enum
from typing import Any

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin


class MessageRole(enum.StrEnum):
    """Role of a chat message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatSession(UUIDMixin, TimestampMixin, Base):
    """
    Chat session model.

    Groups related chat messages into a conversation thread.
    Each user can have multiple concurrent sessions.
    """

    __tablename__ = "chat_sessions"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        default="New Chat",
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, title={self.title})>"


class ChatMessage(UUIDMixin, TimestampMixin, Base):
    """
    Individual chat message model.

    Stores the content, role (user/assistant/system), and any
    source citations retrieved by the RAG pipeline.
    """

    __tablename__ = "chat_messages"

    session_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[MessageRole] = mapped_column(
        SAEnum(MessageRole),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    sources: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Relationship back to session
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, role={self.role})>"
