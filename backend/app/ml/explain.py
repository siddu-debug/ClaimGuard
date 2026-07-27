import numpy as np
import pandas as pd
from typing import Dict, Any, List
from app.ml.features import extract_features_single
from app.ml.predict import get_model_artifact

FEATURE_LABELS = {
    "days_since_policy_start": "Policy Tenure (Days)",
    "claim_amount": "Claim Amount ($)",
    "claim_amount_log": "Log Claim Amount",
    "prior_claims_count": "Prior Claim Count",
    "claim_month": "Claim Month",
    "claim_day_of_week": "Claim Day of Week",
    "amount_to_prior_claims_ratio": "Claim Amount / Prior Claims Ratio",
    "incident_type_auto_collision": "Incident Type: Auto Collision",
    "incident_type_water_damage": "Incident Type: Water Damage",
    "incident_type_theft_burglary": "Incident Type: Theft / Burglary",
    "incident_type_fire_damage": "Incident Type: Fire Damage",
    "incident_type_slip_and_fall": "Incident Type: Slip & Fall",
    "incident_type_hail_damage": "Incident Type: Hail Damage"
}

def get_shap_explanation(claim_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes SHAP feature attribution values for a single claim.
    Returns a dictionary with top risk drivers, base value, and formatted feature impacts.
    """
    artifact = get_model_artifact()
    explainer = artifact["explainer"]
    feature_names = artifact["feature_names"]
    
    features_df = extract_features_single(claim_dict)
    
    # Compute SHAP values
    shap_vals = explainer(features_df)
    
    if hasattr(shap_vals, "values"):
        values = shap_vals.values[0]
        base_val = float(shap_vals.base_values[0]) if hasattr(shap_vals.base_values, "__len__") else float(shap_vals.base_values)
    else:
        values = shap_vals[0]
        base_val = float(explainer.expected_value)
        
    features_impact = []
    for i, col in enumerate(feature_names):
        raw_val = float(features_df.iloc[0][col])
        contrib = float(values[i])
        features_impact.append({
            "feature": col,
            "label": FEATURE_LABELS.get(col, col),
            "raw_value": raw_val,
            "contribution": round(contrib, 4),
            "is_risk_increasing": contrib > 0
        })
        
    # Sort features by absolute SHAP contribution magnitude
    features_impact.sort(key=lambda x: abs(x["contribution"]), reverse=True)
    
    top_positive_drivers = [f for f in features_impact if f["contribution"] > 0][:3]
    top_negative_drivers = [f for f in features_impact if f["contribution"] < 0][:2]
    
    return {
        "base_value": round(base_val, 4),
        "top_features": features_impact[:6],
        "top_risk_increasing_factors": top_positive_drivers,
        "top_risk_decreasing_factors": top_negative_drivers
    }
