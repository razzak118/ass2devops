"""Train, track and register the Student Score Prediction model with MLflow."""
from pathlib import Path
import sys
import numpy as np
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model_utils import STUDY_HOURS, EXAM_SCORES

TRACKING_URI = "sqlite:///mlflow.db"
EXPERIMENT_NAME = "Student Score Prediction"
MODEL_NAME = "StudentScoreModel"


def main():
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    x_train, x_test, y_train, y_test = train_test_split(
        STUDY_HOURS, EXAM_SCORES, test_size=0.25, random_state=42
    )
    model = LinearRegression().fit(x_train, y_train)
    predictions = model.predict(x_test)
    mae = float(mean_absolute_error(y_test, predictions))
    rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
    r2 = float(r2_score(y_test, predictions))

    with mlflow.start_run(run_name="linear-regression-baseline") as run:
        mlflow.log_param("model_type", "LinearRegression")
        mlflow.log_param("training_rows", len(x_train))
        mlflow.log_param("test_rows", len(x_test))
        mlflow.log_param("feature", "study_hours_per_day")
        mlflow.log_param("target", "exam_score_out_of_100")
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=MODEL_NAME,
            serialization_format="cloudpickle",
            input_example=np.array([[4.0]]),
        )
        print("TRAINING_SUCCESS")
        print(f"RUN_ID={run.info.run_id}")
        print(f"MAE={mae:.3f} RMSE={rmse:.3f} R2={r2:.3f}")

    client = MlflowClient(tracking_uri=TRACKING_URI)
    versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    if not versions:
        raise RuntimeError("Model registration did not create a model version")
    latest_version = max(int(v.version) for v in versions)
    Path(__file__).with_name("model_version.txt").write_text(str(latest_version), encoding="utf-8")
    print(f"REGISTERED_MODEL={MODEL_NAME}")
    print(f"MODEL_VERSION={latest_version}")
    print("Metrics and model version are recorded in MLflow.")

if __name__ == "__main__":
    main()
