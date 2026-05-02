"""
Heart disease model training pipeline.

Trains a LightGBM classifier on clinical parameters,
logs metrics to MLflow, and exports local artifacts.
"""

import logging
from pathlib import Path

import joblib
import lightgbm as lgb
import mlflow
import mlflow.lightgbm
import pandas as pd
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_heart_model(
    data_path: str = "ml/data/heart_disease.csv",
    output_path: str = "ml/models/heart_model.pkl",
    mlflow_tracking_uri: str = "http://localhost:5000",
) -> None:
    """
    Train a LightGBM heart disease prediction model.

    Expected dataset: UCI Heart Disease or compatible format
    with clinical features and 'HeartDisease' target column.
    """
    logger.info("Loading dataset from %s", data_path)

    df = pd.read_csv(data_path)
    logger.info("Dataset shape: %s", df.shape)

    # Encode categorical columns if present
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if "HeartDisease" in categorical_cols:
        categorical_cols.remove("HeartDisease")

    for col in categorical_cols:
        df[col] = df[col].astype("category").cat.codes

    X = df.drop("HeartDisease", axis=1)
    y = df["HeartDisease"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y,
    )

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment("heart_disease")

    with mlflow.start_run(run_name="lightgbm_heart"):
        params = {
            "objective": "binary",
            "metric": "auc",
            "n_estimators": 300,
            "max_depth": 8,
            "learning_rate": 0.05,
            "num_leaves": 31,
            "min_child_samples": 20,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "verbosity": -1,
        }

        model = lgb.LGBMClassifier(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
        )

        # Evaluate
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)

        logger.info("Accuracy: %.4f | F1: %.4f | AUC: %.4f", acc, f1, auc)

        # Log to MLflow
        mlflow.log_params(params)
        mlflow.log_metrics({"accuracy": acc, "f1_score": f1, "auc_roc": auc})
        mlflow.lightgbm.log_model(
            model, "model", registered_model_name="heart_disease",
        )

        # Save locally
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, output)
        joblib.dump(list(X.columns), output.parent / "heart_feature_names.pkl")

        logger.info("Model saved to %s", output)


if __name__ == "__main__":
    train_heart_model()
