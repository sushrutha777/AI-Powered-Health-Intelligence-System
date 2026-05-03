"""
Disease prediction model training pipeline.

Trains a RandomForest classifier on symptom-disease mappings,
logs metrics and model to MLflow, and exports local artifacts.
"""

import logging
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_disease_model(
    data_path: str = "ml/data/disease_dataset.csv",
    output_path: str = "ml/models/disease_model.pkl",
    mlflow_tracking_uri: str = "sqlite:///mlflow.db",
) -> None:
    """
    Train a RandomForest disease prediction model.

    Args:
        data_path: Path to the symptom-disease CSV dataset.
        output_path: Path to save the trained model.
        mlflow_tracking_uri: MLflow tracking server URI.
    """
    logger.info("Loading dataset from %s", data_path)

    # Load Data
    # Expected CSV format: columns are symptoms (binary 0/1),
    # last column is 'prognosis' (disease label)
    df = pd.read_csv(data_path)
    logger.info("Dataset shape: %s", df.shape)

    X = df.drop("prognosis", axis=1)
    y = df["prognosis"]

    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # Split Data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded,
    )

    # Train Model
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment("disease_prediction")

    with mlflow.start_run(run_name="random_forest_disease"):
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )

        model.fit(X_train, y_train)

        # Evaluate Model
        train_acc = model.score(X_train, y_train)
        test_acc = model.score(X_test, y_test)
        cv_scores = cross_val_score(model, X, y_encoded, cv=5)

        logger.info("Train accuracy: %.4f", train_acc)
        logger.info("Test accuracy: %.4f", test_acc)
        logger.info("CV mean accuracy: %.4f (+/- %.4f)", cv_scores.mean(), cv_scores.std())

        # Log to MLflow
        mlflow.log_params({
            "n_estimators": 200,
            "max_depth": 20,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "n_features": X.shape[1],
            "n_classes": len(label_encoder.classes_),
        })
        mlflow.log_metrics({
            "train_accuracy": train_acc,
            "test_accuracy": test_acc,
            "cv_mean_accuracy": cv_scores.mean(),
            "cv_std_accuracy": cv_scores.std(),
        })

        mlflow.sklearn.log_model(
            model, "model",
            registered_model_name="disease_predictor",
        )

        # Save Local Artifacts
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, output)

        # Save label encoder alongside
        joblib.dump(label_encoder, output.parent / "disease_label_encoder.pkl")
        joblib.dump(list(X.columns), output.parent / "disease_feature_names.pkl")

        logger.info("Model saved to %s", output)
        logger.info("MLflow run completed")


if __name__ == "__main__":
    train_disease_model()
