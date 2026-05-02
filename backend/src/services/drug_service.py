"""
Drug recommendation service — NLP-based drug matching
using TF-IDF vectorization and cosine similarity.
"""

from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.core.logging import get_logger
from src.schemas.drug import (
    DrugRecommendation, DrugRecommendationInput, DrugRecommendationResponse,
)

logger = get_logger(__name__)

# Placeholder drug database — replaced by real data loader in production
_DRUG_DATABASE: list[dict[str, Any]] = [
    {"name": "Metformin", "condition": "diabetes type 2", "rating": 7.5,
     "review": "Effective for controlling blood sugar levels with minimal side effects.",
     "side_effects": ["nausea", "diarrhea", "stomach upset"]},
    {"name": "Lisinopril", "condition": "hypertension high blood pressure",
     "rating": 8.0, "review": "Well-tolerated ACE inhibitor for blood pressure control.",
     "side_effects": ["dry cough", "dizziness", "headache"]},
    {"name": "Atorvastatin", "condition": "high cholesterol hyperlipidemia",
     "rating": 8.2, "review": "Highly effective statin for cholesterol management.",
     "side_effects": ["muscle pain", "digestive issues", "fatigue"]},
    {"name": "Sertraline", "condition": "depression anxiety disorder",
     "rating": 7.0, "review": "Common SSRI antidepressant with good efficacy.",
     "side_effects": ["nausea", "insomnia", "dizziness", "dry mouth"]},
    {"name": "Omeprazole", "condition": "acid reflux GERD gastroesophageal",
     "rating": 8.5, "review": "Proton pump inhibitor effective for acid reflux.",
     "side_effects": ["headache", "nausea", "abdominal pain"]},
    {"name": "Amlodipine", "condition": "hypertension high blood pressure angina",
     "rating": 7.8, "review": "Calcium channel blocker for hypertension and angina.",
     "side_effects": ["edema", "dizziness", "flushing"]},
    {"name": "Albuterol", "condition": "asthma bronchospasm breathing difficulty",
     "rating": 8.3, "review": "Fast-acting bronchodilator for asthma relief.",
     "side_effects": ["tremor", "nervousness", "headache"]},
    {"name": "Levothyroxine", "condition": "hypothyroidism thyroid underactive",
     "rating": 7.9, "review": "Standard thyroid hormone replacement therapy.",
     "side_effects": ["weight changes", "insomnia", "tremor"]},
    {"name": "Ibuprofen", "condition": "pain inflammation fever arthritis",
     "rating": 7.2, "review": "NSAID for pain relief and inflammation reduction.",
     "side_effects": ["stomach upset", "heartburn", "dizziness"]},
    {"name": "Amoxicillin", "condition": "bacterial infection pneumonia bronchitis",
     "rating": 7.6, "review": "Broad-spectrum antibiotic for bacterial infections.",
     "side_effects": ["diarrhea", "rash", "nausea"]},
]

_vectorizer: TfidfVectorizer | None = None
_tfidf_matrix: Any = None
_is_initialized = False


def _initialize_engine() -> None:
    """Build TF-IDF matrix from drug database."""
    global _vectorizer, _tfidf_matrix, _is_initialized

    if _is_initialized:
        return

    corpus = [
        f"{drug['condition']} {drug.get('review', '')}"
        for drug in _DRUG_DATABASE
    ]

    _vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    _tfidf_matrix = _vectorizer.fit_transform(corpus)
    _is_initialized = True

    logger.info("drug_recommendation_engine_initialized", num_drugs=len(_DRUG_DATABASE))


async def recommend_drugs(input_data: DrugRecommendationInput) -> DrugRecommendationResponse:
    """Find drugs matching the given condition using cosine similarity."""
    _initialize_engine()

    query_text = input_data.condition
    if input_data.symptoms:
        query_text += " " + " ".join(input_data.symptoms)

    query_vector = _vectorizer.transform([query_text])  # type: ignore[union-attr]
    similarities = cosine_similarity(query_vector, _tfidf_matrix).flatten()

    top_indices = np.argsort(similarities)[::-1][: input_data.top_k]

    recommendations = []
    for idx in top_indices:
        if similarities[idx] > 0.01:
            drug = _DRUG_DATABASE[idx]
            recommendations.append(DrugRecommendation(
                drug_name=drug["name"],
                condition=drug["condition"],
                effectiveness_score=float(similarities[idx]),
                rating=drug.get("rating"),
                review_summary=drug.get("review"),
                side_effects=drug.get("side_effects", []),
            ))

    logger.info("drug_recommendation_completed", condition=input_data.condition,
                num_results=len(recommendations))

    return DrugRecommendationResponse(
        condition_query=input_data.condition,
        recommendations=recommendations,
        total_matches=len(recommendations),
        model_info="TF-IDF + Cosine Similarity v1.0",
    )
