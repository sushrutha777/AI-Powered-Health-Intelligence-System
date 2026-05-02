"""
Drug recommendation endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.deps import get_current_user
from src.models.user import User
from src.schemas.drug import DrugRecommendationInput, DrugRecommendationResponse
from src.services.drug_service import recommend_drugs

router = APIRouter(prefix="/drug", tags=["Drug Recommendation"])


@router.post(
    "/recommend",
    response_model=DrugRecommendationResponse,
    summary="Get drug recommendations",
)
async def recommend(
    input_data: DrugRecommendationInput,
    current_user: Annotated[User, Depends(get_current_user)],
) -> DrugRecommendationResponse:
    """Get personalized drug recommendations based on condition."""
    return await recommend_drugs(input_data)
