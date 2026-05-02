"""
Disease prediction service — business logic for symptom-based
disease prediction using RandomForest.

Handles model loading, symptom encoding, inference, and
prediction history management.
"""

import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.core.logging import get_logger
from src.models.prediction import Prediction, PredictionType
from src.schemas.disease import (
    DiseasePredictionResponse,
    DiseasePredictionResult,
    DiseaseSymptomInput,
    PredictionHistoryItem,
    PredictionHistoryResponse,
)

logger = get_logger(__name__)

# ── Symptom and Disease Mappings ─────────────────────────────────────
# These would be loaded from training data in production.
# Placeholder mappings for the scaffold — will be replaced by
# actual encodings from the trained model.

SYMPTOM_LIST = [
    "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing",
    "shivering", "chills", "joint_pain", "stomach_pain", "acidity",
    "ulcers_on_tongue", "muscle_wasting", "vomiting", "burning_micturition",
    "spotting_urination", "fatigue", "weight_gain", "anxiety",
    "cold_hands_and_feets", "mood_swings", "weight_loss", "restlessness",
    "lethargy", "patches_in_throat", "irregular_sugar_level", "cough",
    "high_fever", "sunken_eyes", "breathlessness", "sweating", "dehydration",
    "indigestion", "headache", "yellowish_skin", "dark_urine", "nausea",
    "loss_of_appetite", "pain_behind_the_eyes", "back_pain", "constipation",
    "abdominal_pain", "diarrhoea", "mild_fever", "yellow_urine",
    "yellowing_of_eyes", "acute_liver_failure", "fluid_overload",
    "swelling_of_stomach", "swelled_lymph_nodes", "malaise",
    "blurred_and_distorted_vision", "phlegm", "throat_irritation",
    "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion",
    "chest_pain", "weakness_in_limbs", "fast_heart_rate",
    "pain_during_bowel_movements", "pain_in_anal_region", "bloody_stool",
    "irritation_in_anus", "neck_pain", "dizziness", "cramps", "bruising",
    "obesity", "swollen_legs", "swollen_blood_vessels", "puffy_face_and_eyes",
    "enlarged_thyroid", "brittle_nails", "swollen_extremeties",
    "excessive_hunger", "extra_marital_contacts", "drying_and_tingling_lips",
    "slurred_speech", "knee_pain", "hip_joint_pain", "muscle_weakness",
    "stiff_neck", "swelling_joints", "movement_stiffness",
    "spinning_movements", "loss_of_balance", "unsteadiness",
    "weakness_of_one_body_side", "loss_of_smell", "bladder_discomfort",
    "foul_smell_of_urine", "continuous_feel_of_urine", "passage_of_gases",
    "internal_itching", "toxic_look_(typhos)", "depression", "irritability",
    "muscle_pain", "altered_sensorium", "red_spots_over_body",
    "belly_pain", "abnormal_menstruation", "dischromic_patches",
    "watering_from_eyes", "increased_appetite", "polyuria",
    "family_history", "mucoid_sputum", "rusty_sputum",
    "lack_of_concentration", "visual_disturbances",
    "receiving_blood_transfusion", "receiving_unsterile_injections", "coma",
    "stomach_bleeding", "distention_of_abdomen",
    "history_of_alcohol_consumption", "fluid_overload.1",
    "blood_in_sputum", "prominent_veins_on_calf", "palpitations",
    "painful_walking", "pus_filled_pimples", "blackheads", "scurrying",
    "skin_peeling", "silver_like_dusting", "small_dents_in_nails",
    "inflammatory_nails", "blister", "red_sore_around_nose",
    "yellow_crust_ooze",
]

DISEASE_LIST = [
    "Fungal infection", "Allergy", "GERD", "Chronic cholestasis",
    "Drug Reaction", "Peptic ulcer disease", "AIDS", "Diabetes",
    "Gastroenteritis", "Bronchial Asthma", "Hypertension", "Migraine",
    "Cervical spondylosis", "Paralysis (brain hemorrhage)", "Jaundice",
    "Malaria", "Chicken pox", "Dengue", "Typhoid", "Hepatitis A",
    "Hepatitis B", "Hepatitis C", "Hepatitis D", "Hepatitis E",
    "Alcoholic hepatitis", "Tuberculosis", "Common Cold", "Pneumonia",
    "Dimorphic hemorrhoids (piles)", "Heart attack", "Varicose veins",
    "Hypothyroidism", "Hyperthyroidism", "Hypoglycemia",
    "Osteoarthristis", "Arthritis",
    "(vertigo) Paroxysmal Positional Vertigo", "Acne",
    "Urinary tract infection", "Psoriasis", "Impetigo",
]

DISEASE_DESCRIPTIONS: dict[str, str] = {
    "Fungal infection": "A fungal infection caused by fungi that invade the tissue.",
    "Allergy": "An immune system response to a foreign substance.",
    "GERD": "Gastroesophageal reflux disease — chronic acid reflux.",
    "Diabetes": "A metabolic disease causing high blood sugar levels.",
    "Hypertension": "Persistently elevated blood pressure in arteries.",
    "Migraine": "A neurological condition with intense, debilitating headaches.",
    "Common Cold": "A viral infectious disease of the upper respiratory tract.",
    "Pneumonia": "Infection that inflames air sacs in one or both lungs.",
    "Malaria": "A mosquito-borne infectious disease affecting humans.",
    "Dengue": "A mosquito-borne tropical disease caused by dengue virus.",
    "Typhoid": "A bacterial infection caused by Salmonella typhi.",
}

# ── Model Holder ─────────────────────────────────────────────────────

_model: Any = None
_model_version: str | None = None


def _encode_symptoms(symptoms: list[str]) -> "np.ndarray[Any, np.dtype[np.float32]]":
    """Encode symptom names into a binary feature vector."""
    vector = np.zeros(len(SYMPTOM_LIST), dtype=np.float32)
    symptom_index = {s: i for i, s in enumerate(SYMPTOM_LIST)}

    for symptom in symptoms:
        normalized = symptom.lower().strip().replace(" ", "_")
        if normalized in symptom_index:
            vector[symptom_index[normalized]] = 1.0
        else:
            logger.warning("unknown_symptom", symptom=normalized)

    return vector.reshape(1, -1)


async def load_disease_model() -> None:
    """
    Load the disease prediction model into memory.

    Attempts to load from MLflow first, falls back to local artifact.
    """
    global _model, _model_version

    if _model is not None:
        return

    settings = get_settings()
    local_path = Path("ml/models/disease_model.pkl")

    try:
        # Try MLflow first
        import mlflow

        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        _model = mlflow.pyfunc.load_model("models:/disease_predictor/Production")
        _model_version = "mlflow-production"
        logger.info("disease_model_loaded", source="mlflow")
    except Exception:
        # Fallback to local model file
        if local_path.exists():
            import joblib

            _model = joblib.load(local_path)
            _model_version = "local"
            logger.info("disease_model_loaded", source="local")
        else:
            logger.warning(
                "disease_model_not_found",
                message="No model available — predictions will use fallback logic",
            )


async def predict_disease(
    db: AsyncSession,
    user_id: uuid.UUID,
    input_data: DiseaseSymptomInput,
) -> DiseasePredictionResponse:
    """
    Predict disease from symptoms and persist the result.

    Encodes symptoms into a feature vector, runs inference through
    the RandomForest model, and stores the prediction in the database.
    """
    await load_disease_model()

    features = _encode_symptoms(input_data.symptoms)

    if _model is not None:
        # Real model inference
        probabilities = _model.predict_proba(features)[0]
        top_indices = np.argsort(probabilities)[::-1][:5]

        primary_idx = top_indices[0]
        primary = DiseasePredictionResult(
            disease=DISEASE_LIST[primary_idx],
            confidence=float(probabilities[primary_idx]),
            description=DISEASE_DESCRIPTIONS.get(
                DISEASE_LIST[primary_idx],
                "Consult a healthcare professional for more information.",
            ),
            precautions=[],
        )

        differentials = [
            DiseasePredictionResult(
                disease=DISEASE_LIST[idx],
                confidence=float(probabilities[idx]),
                description=DISEASE_DESCRIPTIONS.get(
                    DISEASE_LIST[idx],
                    "Consult a healthcare professional for more information.",
                ),
                precautions=[],
            )
            for idx in top_indices[1:]
            if probabilities[idx] > 0.05
        ]
    else:
        # Fallback — return placeholder response
        primary = DiseasePredictionResult(
            disease="Model Not Available",
            confidence=0.0,
            description="The disease prediction model is not currently loaded. "
            "Please contact the administrator.",
            precautions=["Consult a healthcare professional"],
        )
        differentials = []

    # Persist prediction
    prediction = Prediction(
        user_id=user_id,
        prediction_type=PredictionType.DISEASE,
        input_data={"symptoms": input_data.symptoms},
        result={
            "primary": primary.model_dump(),
            "differentials": [d.model_dump() for d in differentials],
        },
        confidence=primary.confidence,
        model_version=_model_version,
    )
    db.add(prediction)
    await db.flush()
    await db.refresh(prediction)

    logger.info(
        "disease_prediction_completed",
        prediction_id=str(prediction.id),
        disease=primary.disease,
        confidence=primary.confidence,
    )

    return DiseasePredictionResponse(
        prediction_id=prediction.id,
        primary_prediction=primary,
        differential_diagnoses=differentials,
        model_version=_model_version,
        timestamp=datetime.now(UTC),
    )


async def get_prediction_history(
    db: AsyncSession,
    user_id: uuid.UUID,
    prediction_type: PredictionType | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PredictionHistoryResponse:
    """
    Retrieve paginated prediction history for a user.

    Optionally filters by prediction type (disease/heart).
    """
    query = select(Prediction).where(Prediction.user_id == user_id)
    count_query = select(func.count()).select_from(Prediction).where(
        Prediction.user_id == user_id
    )

    if prediction_type:
        query = query.where(Prediction.prediction_type == prediction_type)
        count_query = count_query.where(
            Prediction.prediction_type == prediction_type
        )

    query = query.order_by(Prediction.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    predictions = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    return PredictionHistoryResponse(
        predictions=[
            PredictionHistoryItem.model_validate(p) for p in predictions
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
