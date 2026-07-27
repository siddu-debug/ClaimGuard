from typing import Dict, Any, Tuple

def decide(ml_score: float, claim_dict: Dict[str, Any]) -> Tuple[str, str]:
    """
    Evaluates business rules layered on top of the ML fraud risk score.
    Returns a tuple of (decision, reasoning).
    Decisions: 'auto_approve' | 'auto_reject' | 'manual_review'
    """
    claim_amount = float(claim_dict.get("claim_amount", 0.0))
    
    # Hard Rule 1: High claim amount threshold > $50,000 mandates human adjuster review
    if claim_amount > 50000.0:
        return "manual_review", f"High claim amount (${claim_amount:,.2f} > $50,000 threshold) mandates manual adjuster review regardless of risk score."

    # ML Score Rule 1: High Fraud Score > 0.8 -> Auto Reject
    if ml_score > 0.80:
        return "auto_reject", f"Elevated fraud probability score of {ml_score:.1%} exceeds automated rejection threshold (0.80)."

    # ML Score Rule 2: Low Fraud Score < 0.2 -> Auto Approve
    if ml_score < 0.20:
        return "auto_approve", f"Low fraud probability score of {ml_score:.1%} satisfies automated approval criteria (< 0.20)."

    # Borderline Score: Manual Review
    return "manual_review", f"Fraud risk score of {ml_score:.1%} falls in borderline review window (0.20 - 0.80)."
