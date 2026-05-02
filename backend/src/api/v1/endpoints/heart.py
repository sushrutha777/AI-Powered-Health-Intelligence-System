"""
Heart disease risk assessment endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.db.session import get_db
from src.models.prediction import PredictionType
from src.models.user import User
from src.schemas.disease import PredictionHistoryResponse
from src.schemas.heart import HeartDiseaseInput, HeartDiseaseResponse
from src.services.disease_service import get_prediction_history
from src.services.heart_service import assess_heart_risk

router = APIRouter(prefix="/heart", tags=["Heart Disease Assessment"])


@router.post(
    "/assess",
    response_model=HeartDiseaseResponse,
    summary="Assess heart disease risk",
)
async def assess(
    input_data: HeartDiseaseInput,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> HeartDiseaseResponse:
    """Submit clinical parameters for heart disease risk assessment."""
    return await assess_heart_risk(db, current_user.id, input_data)


@router.get(
    "/history",
    response_model=PredictionHistoryResponse,
    summary="Get heart assessment history",
)
async def history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PredictionHistoryResponse:
    """Retrieve paginated heart assessment history."""
    return await get_prediction_history(
        db, current_user.id, PredictionType.HEART, page, page_size,
    )
