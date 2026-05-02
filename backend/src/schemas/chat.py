"""
Chat and RAG chatbot Pydantic schemas.

Defines request/response models for the medical chatbot
including message exchange, session management, and source citations.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

# ── Request Schemas ──────────────────────────────────────────────────


class ChatMessageInput(BaseModel):
    """Input schema for sending a chat message."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's message to the medical chatbot",
    )
    session_id: uuid.UUID | None = Field(
        default=None,
        description="Existing session ID. If null, creates a new session.",
    )


# ── Response Schemas ─────────────────────────────────────────────────


class SourceCitation(BaseModel):
    """A source document used to ground the chatbot's response."""

    title: str = Field(..., description="Source document title")
    content_snippet: str = Field(
        ..., description="Relevant snippet from the source"
    )
    relevance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Relevance to the query"
    )


class ChatMessageResponse(BaseModel):
    """Response from the medical chatbot."""

    session_id: uuid.UUID
    message_id: uuid.UUID
    content: str = Field(..., description="Assistant's response text")
    sources: list[SourceCitation] = Field(
        default_factory=list,
        description="Source citations used to generate the response",
    )
    timestamp: datetime


class ChatMessageItem(BaseModel):
    """Single message in chat history."""

    id: uuid.UUID
    role: str
    content: str
    sources: list[SourceCitation] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    """Full chat session history."""

    session_id: uuid.UUID
    title: str
    messages: list[ChatMessageItem]
    created_at: datetime


class ChatSessionItem(BaseModel):
    """Chat session summary for listing."""

    id: uuid.UUID
    title: str
    message_count: int = 0
    last_message_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionListResponse(BaseModel):
    """List of user's chat sessions."""

    sessions: list[ChatSessionItem]
    total: int
