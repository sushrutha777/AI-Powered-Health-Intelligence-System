"""
Chat / RAG chatbot endpoints.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageInput,
    ChatMessageResponse,
    ChatSessionListResponse,
)
from src.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Medical Chatbot"])


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    summary="Send a message to the medical chatbot",
)
async def send_message(
    input_data: ChatMessageInput,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChatMessageResponse:
    """Send a message and receive an AI-generated response with sources."""
    try:
        service = ChatService(db)
        return await service.send_message(current_user.id, input_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get(
    "/sessions",
    response_model=ChatSessionListResponse,
    summary="List chat sessions",
)
async def list_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChatSessionListResponse:
    """List all chat sessions for the authenticated user."""
    service = ChatService(db)
    return await service.list_sessions(current_user.id)


@router.get(
    "/sessions/{session_id}",
    response_model=ChatHistoryResponse,
    summary="Get chat session history",
)
async def get_session(
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChatHistoryResponse:
    """Get full message history for a specific chat session."""
    try:
        service = ChatService(db)
        return await service.get_session_history(session_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chat session",
)
async def delete_session(
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a chat session and all its messages."""
    service = ChatService(db)
    deleted = await service.delete_session(session_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
