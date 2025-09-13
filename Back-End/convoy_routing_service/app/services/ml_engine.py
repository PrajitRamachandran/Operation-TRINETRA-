import lightgbm as lgb
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from ..db import crud, models

# In a real project, this path would point to a model trained on historical data.
MODEL_PATH = "models/lgbm_risk_classifier.txt"
RISK_CLASSES = ['Low', 'Medium', 'High']

try:
    risk_model = lgb.Booster(model_file=MODEL_PATH)
except lgb.basic.LightGBMError:
    print(f"Warning: Model file not found at {MODEL_PATH}. Using dummy prediction logic.")
    risk_model = None

def predict_segment_risk(features: dict) -> tuple[str, float]:
    """Predicts risk using the loaded LightGBM model or dummy logic."""
    if risk_model:
        # Create a feature vector in the correct order for the model
        feature_vector = [features.get(f, 0) for f in risk_model.feature_name()]
        probabilities = risk_model.predict([feature_vector])[0]
    else:
        # Dummy logic if model fails to load
        threat_factor = features.get("threats_within_2km_last_24h", 0)
        base_risk = 0.05 + threat_factor * 0.2
        probabilities = np.array([1.0 - base_risk, base_risk * 0.6, base_risk * 0.4])
        probabilities /= probabilities.sum() # Normalize

    predicted_class_index = np.argmax(probabilities)
    categorical_risk = RISK_CLASSES[predicted_class_index]
    
    # Continuous danger score: P(Medium) * 0.5 + P(High) * 1.0
    danger_score = (probabilities[1] * 0.5) + (probabilities[2] * 1.0)
    
    return categorical_risk, min(1.0, float(danger_score))

def train_new_model():
    """Placeholder for an asynchronous model training job."""
    print("Starting ML model training...")
    # 1. Load historical segment data and threat incidents.
    # 2. Perform feature engineering for each data point.
    # 3. Label data based on outcomes (e.g., segments where incidents occurred are 'High' risk).
    # 4. Train a LightGBM classifier.
    # 5. Save the trained model to MODEL_PATH.
    print("ML model training complete.")