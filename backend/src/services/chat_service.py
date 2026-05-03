"""
Chat service — manages chat sessions and message persistence.

Orchestrates the RAG pipeline for message processing and
handles chat session CRUD operations.
"""

import asyncio
import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.models.chat import ChatMessage, ChatSession, MessageRole
from src.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageInput,
    ChatMessageItem,
    ChatMessageResponse,
    ChatSessionItem,
    ChatSessionListResponse,
    SourceCitation,
)

logger = get_logger(__name__)


class ChatService:
    """Manages chat sessions and message processing."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def send_message(
        self, user_id: uuid.UUID, input_data: ChatMessageInput,
    ) -> ChatMessageResponse:
        """Process user message through RAG and persist both messages."""
        # Get or create session
        if input_data.session_id:
            session = await self._get_session(input_data.session_id, user_id)
            if not session:
                raise ValueError("Chat session not found")
        else:
            session = await self._create_session(user_id, input_data.message[:50])

        # Save user message
        user_msg = ChatMessage(
            session_id=session.id, role=MessageRole.USER,
            content=input_data.message,
        )
        self.db.add(user_msg)

        # Generate RAG response using Gemini pipeline
        try:
            from src.services.rag.gemini_medical_rag import ask_medical_question
            # Run sync RAG pipeline in a thread to avoid blocking the event loop
            response_text = await asyncio.to_thread(
                ask_medical_question, input_data.message
            )
            sources: list[SourceCitation] = []
        except Exception as e:
            logger.error("gemini_rag_error", error=str(e))
            response_text = (
                "I am currently unable to process your request. "
                "Please ensure the Gemini API key is configured "
                "and the FAISS index exists."
            )
            sources = []

        # Save assistant message
        assistant_msg = ChatMessage(
            session_id=session.id, role=MessageRole.ASSISTANT,
            content=response_text,
            sources=None,
        )
        self.db.add(assistant_msg)
        await self.db.flush()
        await self.db.refresh(assistant_msg)

        logger.info("chat_message_processed", session_id=str(session.id))

        return ChatMessageResponse(
            session_id=session.id, message_id=assistant_msg.id,
            content=response_text, sources=sources,
            timestamp=datetime.now(UTC),
        )

    async def list_sessions(self, user_id: uuid.UUID) -> ChatSessionListResponse:
        """List all chat sessions for a user."""
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
        )
        sessions = result.scalars().all()

        items = []
        for s in sessions:
            msg_count = await self.db.execute(
                select(func.count()).select_from(ChatMessage)
                .where(ChatMessage.session_id == s.id)
            )
            count = msg_count.scalar() or 0
            items.append(ChatSessionItem(
                id=s.id, title=s.title, message_count=count,
                created_at=s.created_at,
            ))

        return ChatSessionListResponse(sessions=items, total=len(items))

    async def get_session_history(
        self, session_id: uuid.UUID, user_id: uuid.UUID,
    ) -> ChatHistoryResponse:
        """Get full message history for a session."""
        session = await self._get_session(session_id, user_id)
        if not session:
            raise ValueError("Chat session not found")

        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        messages = result.scalars().all()

        return ChatHistoryResponse(
            session_id=session.id, title=session.title,
            messages=[
                ChatMessageItem(
                    id=m.id, role=m.role.value, content=m.content,
                    sources=[
                        SourceCitation(**s) for s in m.sources if isinstance(s, dict)
                    ] if m.sources else None,
                    created_at=m.created_at,
                )
                for m in messages
            ],
            created_at=session.created_at,
        )

    async def delete_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete a chat session and all its messages."""
        session = await self._get_session(session_id, user_id)
        if not session:
            return False
        await self.db.execute(
            delete(ChatSession).where(ChatSession.id == session_id)
        )
        logger.info("chat_session_deleted", session_id=str(session_id))
        return True

    async def _create_session(self, user_id: uuid.UUID, title: str) -> ChatSession:
        session = ChatSession(user_id=user_id, title=title or "New Chat")
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def _get_session(
        self, session_id: uuid.UUID, user_id: uuid.UUID,
    ) -> ChatSession | None:
        result = await self.db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id, ChatSession.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
