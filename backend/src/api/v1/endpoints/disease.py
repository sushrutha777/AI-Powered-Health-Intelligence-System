"""
Disease prediction endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.db.session import get_db
from src.models.prediction import PredictionType
from src.models.user import User
from src.schemas.disease import (
    DiseasePredictionResponse,
    DiseaseSymptomInput,
    PredictionHistoryResponse,
)
from src.services.disease_service import get_prediction_history, predict_disease

router = APIRouter(prefix="/disease", tags=["Disease Prediction"])


@router.post(
    "/predict",
    response_model=DiseasePredictionResponse,
    summary="Predict disease from symptoms",
)
async def predict(
    input_data: DiseaseSymptomInput,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DiseasePredictionResponse:
    """Submit symptoms and receive a disease prediction with confidence scores."""
    return await predict_disease(db, current_user.id, input_data)


@router.get(
    "/history",
    response_model=PredictionHistoryResponse,
    summary="Get disease prediction history",
)
async def history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PredictionHistoryResponse:
    """Retrieve paginated prediction history for the authenticated user."""
    return await get_prediction_history(
        db, current_user.id, PredictionType.DISEASE, page, page_size,
    )
