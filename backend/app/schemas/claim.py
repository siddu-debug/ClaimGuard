from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ClaimBase(BaseModel):
    policy_id: str = Field(..., example="POL-98231")
    claimant_name: str = Field(..., example="John Doe")
    policy_start_date: str = Field(..., example="2024-01-15")
    claim_date: str = Field(..., example="2024-06-20")
    claim_amount: float = Field(..., example=12500.50)
    incident_type: str = Field(..., example="auto_collision")
    incident_description: Optional[str] = Field(None, example="Rear-ended at traffic signal during light rain.")
    prior_claims_count: int = Field(0, example=1)

class ClaimCreateStructured(ClaimBase):
    claim_id: Optional[str] = None

class ClaimCreateUnstructured(BaseModel):
    raw_text: str = Field(..., example="Claimant John Smith, Policy POL-12345 filed a claim on 2024-07-01 for $45,000 following a sudden water pipe burst in house.")

class ClaimStatusUpdate(BaseModel):
    status: str = Field(..., example="approved")  # approved, rejected, manual_review

class ShapFeatureImpact(BaseModel):
    feature: str
    value: float
    contribution: float
    description: str

class ClaimResponse(ClaimBase):
    id: int
    claim_id: str
    fraud_score: Optional[float] = None
    decision: Optional[str] = None
    status: str
    explanation: Optional[str] = None
    shap_values: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None
    created_at: Optional[Any] = None

    class Config:
        from_attributes = True

class ModelMetricsResponse(BaseModel):
    pr_auc: float
    recall_at_p80: float
    confusion_matrix: List[List[int]]
    training_sample_count: int
    feature_names: List[str]
    model_version: str
