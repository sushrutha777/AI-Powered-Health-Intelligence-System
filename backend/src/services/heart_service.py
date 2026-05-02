"""
Heart disease risk assessment service.

Handles model loading, feature engineering, LightGBM inference,
risk categorization, and contributing factor extraction.
"""

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.core.logging import get_logger
from src.models.prediction import Prediction, PredictionType
from src.schemas.heart import (
    ChestPainType, ContributingFactor, HeartDiseaseInput,
    HeartDiseaseResponse, RestingECG, RiskLevel, STSlope,
)

logger = get_logger(__name__)

CHEST_PAIN_MAP = {
    ChestPainType.TYPICAL_ANGINA: 0, ChestPainType.ATYPICAL_ANGINA: 1,
    ChestPainType.NON_ANGINAL: 2, ChestPainType.ASYMPTOMATIC: 3,
}
RESTING_ECG_MAP = {
    RestingECG.NORMAL: 0, RestingECG.ST_T_ABNORMALITY: 1, RestingECG.LV_HYPERTROPHY: 2,
}
ST_SLOPE_MAP = {STSlope.UPSLOPING: 0, STSlope.FLAT: 1, STSlope.DOWNSLOPING: 2}

RISK_RECOMMENDATIONS = {
    RiskLevel.LOW: "Your heart disease risk appears low. Maintain a healthy lifestyle.",
    RiskLevel.MODERATE: "Moderate risk. Schedule a cardiologist check-up and monitor BP/cholesterol.",
    RiskLevel.HIGH: "Elevated risk detected. Consult a cardiologist for comprehensive evaluation.",
    RiskLevel.CRITICAL: "Critical indicators found. Seek immediate medical attention.",
}

_model: Any = None
_model_version: str | None = None


def _encode_features(data: HeartDiseaseInput) -> np.ndarray:
    return np.array([[
        data.age, data.sex, CHEST_PAIN_MAP[data.chest_pain_type],
        data.resting_bp, data.cholesterol, data.fasting_bs,
        RESTING_ECG_MAP[data.resting_ecg], data.max_hr,
        data.exercise_angina, data.oldpeak, ST_SLOPE_MAP[data.st_slope],
    ]], dtype=np.float32)


def _categorize_risk(score: float) -> RiskLevel:
    if score < 0.25: return RiskLevel.LOW
    if score < 0.50: return RiskLevel.MODERATE
    if score < 0.75: return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def _extract_contributing_factors(data: HeartDiseaseInput) -> list[ContributingFactor]:
    factors: list[ContributingFactor] = []
    if data.age > 55:
        factors.append(ContributingFactor(factor="Age", impact=min(data.age/120, 1.0),
            detail=f"Age {data.age} increases cardiovascular risk."))
    if data.cholesterol > 240:
        factors.append(ContributingFactor(factor="Cholesterol", impact=min(data.cholesterol/600, 1.0),
            detail=f"Cholesterol {data.cholesterol} mg/dl is above recommended."))
    if data.resting_bp > 140:
        factors.append(ContributingFactor(factor="Blood Pressure", impact=min(data.resting_bp/250, 1.0),
            detail=f"Resting BP {data.resting_bp} mmHg indicates hypertension."))
    if data.exercise_angina == 1:
        factors.append(ContributingFactor(factor="Exercise Angina", impact=0.8,
            detail="Exercise-induced angina is a significant cardiac risk indicator."))
    if data.st_slope == STSlope.DOWNSLOPING:
        factors.append(ContributingFactor(factor="ST Slope", impact=0.7,
            detail="Downsloping ST segment suggests myocardial ischemia."))
    factors.sort(key=lambda f: f.impact, reverse=True)
    return factors[:5]


def _heuristic_risk_score(data: HeartDiseaseInput) -> float:
    score = 0.0
    if data.age > 55: score += 0.15
    elif data.age > 45: score += 0.08
    if data.sex == 1: score += 0.05
    if data.cholesterol > 240: score += 0.15
    elif data.cholesterol > 200: score += 0.08
    if data.resting_bp > 140: score += 0.12
    if data.exercise_angina == 1: score += 0.15
    if data.fasting_bs == 1: score += 0.08
    if data.st_slope == STSlope.DOWNSLOPING: score += 0.12
    if data.oldpeak > 2.0: score += 0.10
    return min(score, 1.0)


async def load_heart_model() -> None:
    global _model, _model_version
    if _model is not None:
        return
    settings = get_settings()
    local_path = Path("ml/models/heart_model.pkl")
    try:
        import mlflow
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        _model = mlflow.pyfunc.load_model("models:/heart_disease/Production")
        _model_version = "mlflow-production"
        logger.info("heart_model_loaded", source="mlflow")
    except Exception:
        if local_path.exists():
            import joblib
            _model = joblib.load(local_path)
            _model_version = "local"
            logger.info("heart_model_loaded", source="local")
        else:
            logger.warning("heart_model_not_found")


async def assess_heart_risk(
    db: AsyncSession, user_id: uuid.UUID, input_data: HeartDiseaseInput,
) -> HeartDiseaseResponse:
    await load_heart_model()
    features = _encode_features(input_data)

    if _model is not None:
        try:
            risk_score = float(_model.predict_proba(features)[0][1])
        except AttributeError:
            risk_score = float(_model.predict(features)[0])
    else:
        risk_score = _heuristic_risk_score(input_data)

    risk_level = _categorize_risk(risk_score)
    contributing_factors = _extract_contributing_factors(input_data)

    prediction = Prediction(
        user_id=user_id, prediction_type=PredictionType.HEART,
        input_data=input_data.model_dump(),
        result={"risk_score": risk_score, "risk_level": risk_level.value,
                "contributing_factors": [f.model_dump() for f in contributing_factors]},
        confidence=risk_score, model_version=_model_version,
    )
    db.add(prediction)
    await db.flush()
    await db.refresh(prediction)

    logger.info("heart_assessment_completed", prediction_id=str(prediction.id),
                risk_level=risk_level.value, risk_score=risk_score)

    return HeartDiseaseResponse(
        prediction_id=prediction.id, risk_score=risk_score,
        risk_level=risk_level, contributing_factors=contributing_factors,
        recommendation=RISK_RECOMMENDATIONS[risk_level],
        model_version=_model_version, timestamp=datetime.now(timezone.utc),
    )
