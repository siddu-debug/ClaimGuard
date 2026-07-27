import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ml.predict import predict_fraud_score
from app.rules.engine import decide

def test_high_vs_low_risk_scoring():
    """
    Unit test ensuring a high-risk claim (short policy tenure, high claim amount, multiple prior claims)
    scores significantly higher than a low-risk claim (long tenure, low amount, 0 prior claims).
    """
    high_risk_claim = {
        "policy_id": "POL-8899",
        "claimant_name": "Suspicious Subject",
        "policy_start_date": "2024-05-01",
        "claim_date": "2024-05-05",  # 4 days gap
        "claim_amount": 48000.0,
        "incident_type": "fire_damage",
        "incident_description": "Total loss kitchen fire",
        "prior_claims_count": 4
    }

    low_risk_claim = {
        "policy_id": "POL-1122",
        "claimant_name": "Loyal Customer",
        "policy_start_date": "2020-01-01",
        "claim_date": "2024-05-05",  # 1586 days gap
        "claim_amount": 1200.0,
        "incident_type": "auto_collision",
        "incident_description": "Minor parking lot dent",
        "prior_claims_count": 0
    }

    high_score = predict_fraud_score(high_risk_claim)
    low_score = predict_fraud_score(low_risk_claim)

    print(f"High risk score: {high_score}, Low risk score: {low_score}")
    assert high_score > low_score, f"Expected high risk score ({high_score}) > low risk score ({low_score})"
    assert high_score > 0.40, f"Expected high risk score > 0.40, got {high_score}"

def test_rules_engine_hard_cap():
    """
    Test that claims > $50,000 trigger manual_review rule override regardless of ML score.
    """
    huge_claim = {
        "claim_amount": 75000.0,
        "policy_start_date": "2020-01-01",
        "claim_date": "2024-01-01",
        "prior_claims_count": 0
    }
    decision, reason = decide(0.05, huge_claim)  # Low ML score, high amount
    assert decision == "manual_review"
    assert "$50,000 threshold" in reason
