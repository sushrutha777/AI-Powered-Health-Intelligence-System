"""
Disease prediction Pydantic schemas.

Defines request/response models for the general disease
prediction service powered by RandomForest.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DiseaseSymptomInput(BaseModel):
    """Input schema for disease prediction — list of symptoms."""

    symptoms: list[str] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="List of symptom names (e.g., ['headache', 'fever', 'cough'])",
        examples=[["headache", "fever", "fatigue", "nausea"]],
    )


class DiseasePredictionResult(BaseModel):
    """Single disease prediction with confidence."""

    disease: str = Field(..., description="Predicted disease name")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Prediction confidence score"
    )
    description: str = Field(
        ..., description="Brief description of the predicted disease"
    )
    precautions: list[str] = Field(
        default_factory=list, description="Recommended precautions"
    )


class DiseasePredictionResponse(BaseModel):
    """Full disease prediction response."""

    prediction_id: uuid.UUID
    primary_prediction: DiseasePredictionResult
    differential_diagnoses: list[DiseasePredictionResult] = Field(
        default_factory=list,
        max_length=5,
        description="Alternative possible diagnoses ranked by confidence",
    )
    model_version: str | None = None
    timestamp: datetime


class PredictionHistoryItem(BaseModel):
    """Single prediction history entry."""

    id: uuid.UUID
    prediction_type: str
    input_data: dict
    result: dict
    confidence: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PredictionHistoryResponse(BaseModel):
    """Paginated prediction history response."""

    predictions: list[PredictionHistoryItem]
    total: int
    page: int
    page_size: int
