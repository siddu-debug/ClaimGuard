import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Claim
from app.schemas.claim import (
    ClaimCreateStructured,
    ClaimCreateUnstructured,
    ClaimResponse,
    ClaimStatusUpdate
)
from app.ml.predict import predict_fraud_score
from app.ml.explain import get_shap_explanation
from app.ml.features import extract_features_single
from app.rules.engine import decide
from app.core.groq_client import extract_claim_fields, generate_explanation

router = APIRouter(prefix="/claims", tags=["Claims"])

@router.post("", response_model=ClaimResponse)
def create_claim(
    claim_in: ClaimCreateStructured,
    db: Session = Depends(get_db)
):
    """
    Ingests a structured claim, scores it with XGBoost ML + SHAP, runs the rules engine,
    generates a Groq LLM plain-English summary, stores it in DB, and returns the evaluation.
    """
    claim_dict = claim_in.model_dump()
    
    # Generate unique claim_id if missing
    if not claim_dict.get("claim_id"):
        claim_dict["claim_id"] = f"CLM-{random.randint(100000, 999999)}"

    # Feature preparation & ML score calculation
    feat_df = extract_features_single(claim_dict)
    claim_dict["days_since_policy_start"] = int(feat_df.iloc[0]["days_since_policy_start"])
    
    ml_score = predict_fraud_score(claim_dict)
    
    # SHAP feature attribution
    shap_data = get_shap_explanation(claim_dict)
    
    # Rules engine decision
    decision, decision_reason = decide(ml_score, claim_dict)
    
    # Groq narrative explanation
    explanation = generate_explanation(claim_dict, shap_data, ml_score)
    
    # Persist to database
    db_claim = Claim(
        claim_id=claim_dict["claim_id"],
        policy_id=claim_dict["policy_id"],
        claimant_name=claim_dict["claimant_name"],
        policy_start_date=claim_dict["policy_start_date"],
        claim_date=claim_dict["claim_date"],
        claim_amount=claim_dict["claim_amount"],
        incident_type=claim_dict["incident_type"],
        incident_description=claim_dict.get("incident_description"),
        prior_claims_count=claim_dict.get("prior_claims_count", 0),
        fraud_score=ml_score,
        decision=decision,
        status=decision,
        explanation=explanation,
        shap_values=shap_data,
        raw_text=None
    )
    
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    
    return db_claim

@router.post("/unstructured", response_model=ClaimResponse)
def create_unstructured_claim(
    payload: ClaimCreateUnstructured,
    db: Session = Depends(get_db)
):
    """
    Extracts structured fields from raw claim narrative using Groq LLM (llama-3.3-70b-versatile),
    then runs full scoring, rules, and explanation pipeline.
    """
    extracted_fields = extract_claim_fields(payload.raw_text)
    
    # Create structured claim object
    structured_claim = ClaimCreateStructured(
        claim_id=extracted_fields.get("claim_id") or f"CLM-{random.randint(100000, 999999)}",
        policy_id=extracted_fields.get("policy_id", "POL-10001"),
        claimant_name=extracted_fields.get("claimant_name", "Anonymous Claimant"),
        policy_start_date=extracted_fields.get("policy_start_date", "2024-01-01"),
        claim_date=extracted_fields.get("claim_date", "2024-06-01"),
        claim_amount=float(extracted_fields.get("claim_amount", 5000.0)),
        incident_type=extracted_fields.get("incident_type", "auto_collision"),
        incident_description=payload.raw_text,
        prior_claims_count=int(extracted_fields.get("prior_claims_count", 0))
    )
    
    db_claim = create_claim(structured_claim, db)
    db_claim.raw_text = payload.raw_text
    db.commit()
    db.refresh(db_claim)
    return db_claim

@router.get("", response_model=List[ClaimResponse])
def list_claims(
    status: Optional[str] = Query(None, description="Filter by status (auto_approve, auto_reject, manual_review, approved, rejected)"),
    min_score: Optional[float] = Query(None, description="Filter by minimum fraud score threshold"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Paginated list of claims with optional status and min_score filters.
    """
    query = db.query(Claim)
    
    if status:
        query = query.filter(Claim.status == status)
        
    if min_score is not None:
        query = query.filter(Claim.fraud_score >= min_score)
        
    query = query.order_by(Claim.created_at.desc())
    claims = query.offset(offset).limit(limit).all()
    return claims

@router.get("/{claim_db_id}", response_model=ClaimResponse)
def get_claim_detail(
    claim_db_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve full claim details by Database ID, including score, SHAP explanation, and narrative text.
    """
    claim = db.query(Claim).filter(Claim.id == claim_db_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim with ID {claim_db_id} not found.")
    return claim

@router.patch("/{claim_db_id}/status", response_model=ClaimResponse)
def update_claim_status(
    claim_db_id: int,
    status_update: ClaimStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Adjuster manual status override (e.g. approve or reject a claim undergoing manual review).
    """
    claim = db.query(Claim).filter(Claim.id == claim_db_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim with ID {claim_db_id} not found.")
        
    valid_statuses = ["auto_approve", "auto_reject", "manual_review", "approved", "rejected"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status '{status_update.status}'. Allowed: {valid_statuses}")
        
    claim.status = status_update.status
    db.commit()
    db.refresh(claim)
    return claim
