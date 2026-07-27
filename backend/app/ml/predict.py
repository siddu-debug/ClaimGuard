import joblib
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple
from app.core.config import settings
from app.ml.features import extract_features_single

_model_cache = None

def get_model_artifact():
    global _model_cache
    if _model_cache is not None:
        return _model_cache

    model_path = settings.MODEL_PATH
    if not model_path.exists():
        print("Model file not found. Running training script...")
        from app.ml.train import train_fraud_model
        train_fraud_model()

    _model_cache = joblib.load(model_path)
    return _model_cache

def predict_fraud_score(claim_dict: Dict[str, Any]) -> float:
    """
    Predicts fraud risk probability (0.0 to 1.0) for a given claim.
    """
    artifact = get_model_artifact()
    model = artifact["model"]
    
    features_df = extract_features_single(claim_dict)
    prob = float(model.predict_proba(features_df)[0, 1])
    return round(prob, 4)
