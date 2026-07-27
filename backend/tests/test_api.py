import sys
from pathlib import Path
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}

def test_model_metrics_endpoint():
    response = client.get("/model-metrics")
    assert response.status_code == 200
    data = response.json()
    assert "pr_auc" in data
    assert "confusion_matrix" in data
    assert "feature_names" in data

@patch("app.core.groq_client.get_groq_client", return_value=None)
def test_create_and_get_claim(mock_groq):
    """
    Test creating a structured claim, checking its score & decision, and retrieving it.
    """
    payload = {
        "policy_id": "POL-99123",
        "claimant_name": "Alice Smith",
        "policy_start_date": "2023-01-10",
        "claim_date": "2024-03-15",
        "claim_amount": 14500.0,
        "incident_type": "water_damage",
        "incident_description": "Water pipe leak under bathroom sink",
        "prior_claims_count": 1
    }
    
    # POST /claims
    response = client.post("/claims", json=payload)
    assert response.status_code == 200
    created = response.json()
    assert created["policy_id"] == "POL-99123"
    assert created["claimant_name"] == "Alice Smith"
    assert "fraud_score" in created
    assert "decision" in created
    assert "explanation" in created
    
    claim_id = created["id"]
    
    # GET /claims/{id}
    detail_res = client.get(f"/claims/{claim_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == claim_id
    
    # PATCH /claims/{id}/status
    patch_res = client.patch(f"/claims/{claim_id}/status", json={"status": "approved"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "approved"

@patch("app.core.groq_client.get_groq_client", return_value=None)
def test_unstructured_claim_ingestion(mock_groq):
    """
    Test unstructured text ingestion using fallback parsing when Groq is mocked/unavailable.
    """
    raw_text = "Claimant Bob Johnson, policy POL-55443 filed a claim on 2024-05-10 for $32,000 following a sudden garage fire."
    response = client.post("/claims/unstructured", json={"raw_text": raw_text})
    assert response.status_code == 200
    created = response.json()
    assert created["claim_amount"] == 32000.0
    assert "fraud_score" in created
