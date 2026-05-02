"""
Heart disease risk assessment Pydantic schemas.

Defines input parameters matching clinical measurements and
output schemas for risk categorization with contributing factors.
"""

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ChestPainType(StrEnum):
    """Types of chest pain for clinical classification."""

    TYPICAL_ANGINA = "typical_angina"
    ATYPICAL_ANGINA = "atypical_angina"
    NON_ANGINAL = "non_anginal"
    ASYMPTOMATIC = "asymptomatic"


class RestingECG(StrEnum):
    """Resting electrocardiogram results."""

    NORMAL = "normal"
    ST_T_ABNORMALITY = "st_t_abnormality"
    LV_HYPERTROPHY = "lv_hypertrophy"


class STSlope(StrEnum):
    """ST segment slope during exercise."""

    UPSLOPING = "upsloping"
    FLAT = "flat"
    DOWNSLOPING = "downsloping"


class RiskLevel(StrEnum):
    """Heart disease risk categorization."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class HeartDiseaseInput(BaseModel):
    """Clinical parameters for heart disease risk assessment."""

    age: int = Field(..., ge=1, le=120, description="Patient age in years")
    sex: int = Field(..., ge=0, le=1, description="Sex (0=Female, 1=Male)")
    chest_pain_type: ChestPainType = Field(
        ..., description="Type of chest pain experienced"
    )
    resting_bp: int = Field(
        ..., ge=50, le=250, description="Resting blood pressure (mm Hg)"
    )
    cholesterol: int = Field(
        ..., ge=50, le=600, description="Serum cholesterol (mg/dl)"
    )
    fasting_bs: int = Field(
        ...,
        ge=0,
        le=1,
        description="Fasting blood sugar > 120 mg/dl (1=true, 0=false)",
    )
    resting_ecg: RestingECG = Field(
        ..., description="Resting electrocardiogram results"
    )
    max_hr: int = Field(
        ..., ge=50, le=250, description="Maximum heart rate achieved"
    )
    exercise_angina: int = Field(
        ..., ge=0, le=1, description="Exercise-induced angina (1=yes, 0=no)"
    )
    oldpeak: float = Field(
        ..., ge=-5.0, le=10.0, description="ST depression induced by exercise"
    )
    st_slope: STSlope = Field(
        ..., description="Slope of peak exercise ST segment"
    )


class ContributingFactor(BaseModel):
    """A factor contributing to the risk assessment."""

    factor: str = Field(..., description="Name of the contributing factor")
    impact: float = Field(
        ..., ge=0.0, le=1.0, description="Relative impact on the risk score"
    )
    detail: str = Field(
        ..., description="Explanation of why this factor is significant"
    )


class HeartDiseaseResponse(BaseModel):
    """Heart disease risk assessment result."""

    prediction_id: uuid.UUID
    risk_score: float = Field(
        ..., ge=0.0, le=1.0, description="Overall risk score (0=safe, 1=high risk)"
    )
    risk_level: RiskLevel = Field(
        ..., description="Categorized risk level"
    )
    contributing_factors: list[ContributingFactor] = Field(
        default_factory=list,
        description="Top factors contributing to the risk score",
    )
    recommendation: str = Field(
        ..., description="General health recommendation based on risk level"
    )
    model_version: str | None = None
    timestamp: datetime
