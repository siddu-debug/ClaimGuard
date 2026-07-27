import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

FEATURE_COLUMNS = [
    "days_since_policy_start",
    "claim_amount",
    "claim_amount_log",
    "prior_claims_count",
    "claim_month",
    "claim_day_of_week",
    "amount_to_prior_claims_ratio",
    "incident_type_auto_collision",
    "incident_type_water_damage",
    "incident_type_theft_burglary",
    "incident_type_fire_damage",
    "incident_type_slip_and_fall",
    "incident_type_hail_damage"
]

INCIDENT_TYPES = [
    "auto_collision",
    "water_damage",
    "theft_burglary",
    "fire_damage",
    "slip_and_fall",
    "hail_damage"
]

def parse_date(date_str: str) -> datetime:
    if isinstance(date_str, datetime):
        return date_str
    try:
        return datetime.strptime(str(date_str).split("T")[0], "%Y-%m-%d")
    except Exception:
        return datetime.now()

def extract_features_single(claim_dict: Dict[str, Any]) -> pd.DataFrame:
    """
    Transforms a single claim input dictionary into a single-row Pandas DataFrame of ML features.
    """
    p_start = parse_date(claim_dict.get("policy_start_date", "2024-01-01"))
    c_date = parse_date(claim_dict.get("claim_date", "2024-06-01"))
    
    days_since_policy_start = max(0, (c_date - p_start).days)
    claim_amount = float(claim_dict.get("claim_amount", 0.0))
    prior_claims_count = int(claim_dict.get("prior_claims_count", 0))
    
    row = {
        "days_since_policy_start": days_since_policy_start,
        "claim_amount": claim_amount,
        "claim_amount_log": np.log1p(claim_amount),
        "prior_claims_count": prior_claims_count,
        "claim_month": c_date.month,
        "claim_day_of_week": c_date.weekday(),
        "amount_to_prior_claims_ratio": claim_amount / (prior_claims_count + 1)
    }
    
    inc_type = str(claim_dict.get("incident_type", "")).lower()
    for it in INCIDENT_TYPES:
        row[f"incident_type_{it}"] = 1.0 if inc_type == it else 0.0
        
    df = pd.DataFrame([row])
    return df[FEATURE_COLUMNS]

def extract_features_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms a batch dataset of claims into engineered feature columns.
    """
    feature_rows = []
    for _, row in df.iterrows():
        single_df = extract_features_single(row.to_dict())
        feature_rows.append(single_df.iloc[0])
        
    res_df = pd.DataFrame(feature_rows)
    return res_df[FEATURE_COLUMNS]
