"""Shared, deterministic model for the web application and MLflow demo."""
from functools import lru_cache
import numpy as np
from sklearn.linear_model import LinearRegression

# Toy teaching data: daily study hours versus exam score out of 100.
STUDY_HOURS = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16], dtype=float).reshape(-1, 1)
EXAM_SCORES = np.array([18, 23, 29, 34, 40, 46, 52, 57, 63, 68, 74, 83, 91, 98], dtype=float)

@lru_cache(maxsize=1)
def build_model() -> LinearRegression:
    model = LinearRegression()
    model.fit(STUDY_HOURS, EXAM_SCORES)
    return model

def predict_score(model: LinearRegression, study_hours: float) -> float:
    score = float(model.predict(np.array([[study_hours]], dtype=float))[0])
    return min(100.0, max(0.0, score))
