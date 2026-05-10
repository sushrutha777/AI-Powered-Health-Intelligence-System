"""
Drug recommendation service — NLP-based drug matching
using TF-IDF vectorization and cosine similarity.
"""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.core.logging import get_logger
from src.schemas.drug import (
    DrugRecommendation,
    DrugRecommendationInput,
    DrugRecommendationResponse,
)

logger = get_logger(__name__)



_DRUG_DATABASE: list[dict[str, Any]] = []
_vectorizer: TfidfVectorizer | None = None
_tfidf_matrix: Any = None
_is_initialized = False

def _initialize_engine() -> None:
    """Load drug dataset from CSV and build TF-IDF matrix."""
    global _DRUG_DATABASE, _vectorizer, _tfidf_matrix, _is_initialized

    if _is_initialized:
        return

    csv_path = Path("ml/data/drug_dataset.csv")
    if not csv_path.exists():
        logger.warning("drug_dataset_missing", path=str(csv_path))
        _is_initialized = True
        return

    df = pd.read_csv(csv_path)
    # Take a sample to keep memory usage low (e.g., 20000 rows)
    # df = df.sample(n=min(len(df), 20000), random_state=42).reset_index(drop=True)
    # The dataset might be large, but TF-IDF on 160k rows with max_features=5000 is usually fine.

    # Pre-build our database structure
    _DRUG_DATABASE = []
    corpus = []

    for _, row in df.iterrows():
        condition = str(row.get('condition', ''))
        review = str(row.get('review', ''))
        drug_name = str(row.get('drugName', ''))
        rating = row.get('rating', None)
        rating = float(rating) if not pd.isna(rating) else None

        _DRUG_DATABASE.append({
            "name": drug_name,
            "condition": condition,
            "rating": rating,
            "review": review[:200] + "..." if len(review) > 200 else review,
            "side_effects": [],  # Not in dataset
        })
        corpus.append(f"{condition} {review}")

    _vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    _tfidf_matrix = _vectorizer.fit_transform(corpus)
    _is_initialized = True

    logger.info("drug_recommendation_engine_initialized", num_drugs=len(_DRUG_DATABASE))


async def recommend_drugs(input_data: DrugRecommendationInput) -> DrugRecommendationResponse:
    """Find drugs matching the given condition using cosine similarity."""
    _initialize_engine()

    if _vectorizer is None or _tfidf_matrix is None:
        return DrugRecommendationResponse(
            condition_query=input_data.condition,
            recommendations=[
                DrugRecommendation(
                    drug_name="Acetaminophen (Fallback)",
                    condition=input_data.condition,
                    effectiveness_score=0.99,
                    review_summary="Drug database is missing. This is a generic fallback recommendation.",
                )
            ],
            total_matches=1,
            model_info="Fallback System",
        )

    query_text = input_data.condition
    if input_data.symptoms:
        query_text += " " + " ".join(input_data.symptoms)

    query_vector = _vectorizer.transform([query_text])
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
