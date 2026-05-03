"""
Dashboard stats endpoint — provides aggregate counts for the dashboard.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.db.session import get_db
from src.models.chat import ChatSession
from src.models.prediction import Prediction
from src.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class DashboardStats(BaseModel):
    """Aggregate counts for the user dashboard."""

    disease_predictions: int
    chat_sessions: int


@router.get(
    "/stats",
    response_model=DashboardStats,
    summary="Get dashboard statistics",
)
async def get_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DashboardStats:
    """Return aggregate counts for the authenticated user's dashboard."""
    # Disease prediction count
    pred_result = await db.execute(
        select(func.count()).select_from(Prediction).where(
            Prediction.user_id == current_user.id
        )
    )
    pred_count = pred_result.scalar() or 0

    # Chat session count
    chat_result = await db.execute(
        select(func.count()).select_from(ChatSession).where(
            ChatSession.user_id == current_user.id
        )
    )
    chat_count = chat_result.scalar() or 0

    return DashboardStats(
        disease_predictions=pred_count,
        chat_sessions=chat_count,
    )
