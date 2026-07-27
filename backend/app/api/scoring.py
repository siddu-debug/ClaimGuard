import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Claim
from app.core.config import settings
from app.ml.explain import get_shap_explanation
from app.ml.predict import predict_fraud_score
from app.rules.engine import decide
from app.schemas.claim import ModelMetricsResponse

router = APIRouter(tags=["Scoring & Model Metrics"])

@router.get("/claims/{claim_db_id}/score")
def score_claim_endpoint(
    claim_db_id: int,
    db: Session = Depends(get_db)
):
    """
    Computes real-time ML score, SHAP attribution breakdown, and rules engine output for an existing claim.
    """
    claim = db.query(Claim).filter(Claim.id == claim_db_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim ID {claim_db_id} not found.")

    claim_dict = {
        "claim_id": claim.claim_id,
        "policy_id": claim.policy_id,
        "claimant_name": claim.claimant_name,
        "policy_start_date": claim.policy_start_date,
        "claim_date": claim.claim_date,
        "claim_amount": claim.claim_amount,
        "incident_type": claim.incident_type,
        "incident_description": claim.incident_description,
        "prior_claims_count": claim.prior_claims_count
    }

    ml_score = predict_fraud_score(claim_dict)
    shap_data = get_shap_explanation(claim_dict)
    decision, reason = decide(ml_score, claim_dict)

    return {
        "claim_id": claim.claim_id,
        "fraud_score": ml_score,
        "decision": decision,
        "decision_reason": reason,
        "shap_explanation": shap_data
    }

@router.get("/model-metrics", response_model=ModelMetricsResponse)
def get_model_metrics():
    """
    Returns stored offline training metrics (PR-AUC, recall@P0.8, confusion matrix, feature list).
    """
    metrics_path = settings.METRICS_PATH
    if not metrics_path.exists():
        # If metrics.json doesn't exist yet, run training
        from app.ml.train import train_fraud_model
        train_fraud_model()

    with open(metrics_path, "r") as f:
        metrics_data = json.load(f)

    return metrics_data
