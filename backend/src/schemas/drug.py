"""
Drug recommendation Pydantic schemas.

Defines request/response models for the NLP-based drug
recommendation engine using TF-IDF + cosine similarity.
"""

from pydantic import BaseModel, Field


class DrugRecommendationInput(BaseModel):
    """Input schema for drug recommendation."""

    condition: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Medical condition or disease name",
        examples=["diabetes", "hypertension", "depression"],
    )
    symptoms: list[str] | None = Field(
        default=None,
        description="Optional additional symptoms for better matching",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of drug recommendations to return",
    )


class DrugRecommendation(BaseModel):
    """Single drug recommendation with details."""

    drug_name: str = Field(..., description="Name of the recommended drug")
    condition: str = Field(..., description="Target medical condition")
    effectiveness_score: float = Field(
        ..., ge=0.0, le=1.0, description="Cosine similarity score"
    )
    rating: float | None = Field(
        default=None, ge=0.0, le=10.0, description="Average user rating"
    )
    useful_count: int | None = Field(
        default=None, description="Number of users who found the review useful"
    )
    review_summary: str | None = Field(
        default=None, description="Summarized user review"
    )
    side_effects: list[str] = Field(
        default_factory=list, description="Known common side effects"
    )


class DrugRecommendationResponse(BaseModel):
    """Full drug recommendation response."""

    condition_query: str
    recommendations: list[DrugRecommendation]
    total_matches: int
    model_info: str | None = Field(
        default=None, description="TF-IDF model version info"
    )


class DrugDetailResponse(BaseModel):
    """Detailed drug information."""

    drug_name: str
    conditions: list[str]
    avg_rating: float | None = None
    total_reviews: int = 0
    review_summary: str | None = None
    side_effects: list[str] = Field(default_factory=list)
