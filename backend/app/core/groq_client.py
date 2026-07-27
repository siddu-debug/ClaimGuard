import os
import json
import re
from typing import Dict, Any, Optional
from app.core.config import settings

# Attempt to import groq SDK
try:
    from groq import Groq
    _groq_available = True
except ImportError:
    _groq_available = False

def get_groq_client() -> Optional[Any]:
    if not _groq_available:
        return None
    api_key = settings.GROQ_API_KEY
    if not api_key or api_key == "gsk_your_groq_api_key_here":
        return None
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")
        return None

def extract_claim_fields(raw_text: str) -> Dict[str, Any]:
    """
    Extracts structured claim fields from unformatted claim narrative text using Groq LLM (llama-3.3-70b-versatile).
    Falls back to heuristic regex parsing if Groq is unavailable.
    """
    client = get_groq_client()
    
    if client is not None:
        try:
            system_prompt = (
                "You are an expert insurance claim AI parser. Extract the following fields from the free-text claim narrative: "
                "claimant_name, policy_id, policy_start_date, claim_date, claim_amount, incident_type, incident_description, prior_claims_count. "
                "Map incident_type to one of: ['auto_collision', 'water_damage', 'theft_burglary', 'fire_damage', 'slip_and_fall', 'hail_damage']. "
                "Format dates as YYYY-MM-DD (estimate reasonable dates if unspecified). "
                "Output ONLY a raw, valid JSON object without markdown formatting, code blocks, or explanatory prose."
            )
            
            completion = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract fields from this claim description:\n{raw_text}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            response_text = completion.choices[0].message.content.strip()
            # Clean possible markdown wrapping ```json ... ```
            clean_json_str = re.sub(r"^```(json)?|```$", "", response_text, flags=re.MULTILINE).strip()
            extracted = json.loads(clean_json_str)
            return extracted
        except Exception as e:
            print(f"Groq field extraction failed/fallback: {e}")

    # Heuristic Fallback
    return fallback_extract_fields(raw_text)

def fallback_extract_fields(raw_text: str) -> Dict[str, Any]:
    """Fallback regex extractor when LLM is unavailable."""
    # Extract amount ($XX,XXX)
    amount_match = re.search(r"\$\s?([0-9,]+(?:\.[0-9]{2})?)", raw_text)
    amount = float(amount_match.group(1).replace(",", "")) if amount_match else 5000.0
    
    # Extract policy ID
    policy_match = re.search(r"(POL-\d+|policy\s*#?\s*\w+)", raw_text, re.IGNORECASE)
    policy_id = policy_match.group(1).upper() if policy_match else "POL-99999"
    
    # Extract claimant name
    name_match = re.search(r"(claimant|holder|name|mr\.|ms\.)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)", raw_text, re.IGNORECASE)
    claimant_name = name_match.group(2) if name_match else "Jane Doe"
    
    # Determine incident type
    text_lower = raw_text.lower()
    if any(k in text_lower for k in ["pipe", "water", "leak", "flood"]):
        inc_type = "water_damage"
    elif any(k in text_lower for k in ["crash", "collision", "car", "hit", "vehicle", "rear"]):
        inc_type = "auto_collision"
    elif any(k in text_lower for k in ["theft", "stolen", "burglar", "robbery"]):
        inc_type = "theft_burglary"
    elif any(k in text_lower for k in ["fire", "burn", "smoke"]):
        inc_type = "fire_damage"
    elif any(k in text_lower for k in ["slip", "fall", "trip"]):
        inc_type = "slip_and_fall"
    else:
        inc_type = "hail_damage"

    return {
        "claimant_name": claimant_name,
        "policy_id": policy_id,
        "policy_start_date": "2024-01-01",
        "claim_date": "2024-06-15",
        "claim_amount": amount,
        "incident_type": inc_type,
        "incident_description": raw_text[:250],
        "prior_claims_count": 0
    }

def generate_explanation(claim: Dict[str, Any], shap_values: Dict[str, Any], ml_score: float) -> str:
    """
    Generates a 2-3 sentence human-readable narrative explaining why the claim received its fraud risk score.
    Combines SHAP risk factors with claim context.
    """
    client = get_groq_client()
    top_factors = shap_values.get("top_risk_increasing_factors", [])
    factor_descriptions = [
        f"{f['label']} (impact: +{f['contribution']:.2f}, val: {f['raw_value']})"
        for f in top_factors
    ]
    factors_str = ", ".join(factor_descriptions) if factor_descriptions else "standard risk baseline"
    
    if client is not None:
        try:
            prompt = (
                f"You are an AI claims adjuster assistant. Write a concise 2-3 sentence professional summary explaining a claim's fraud risk score.\n"
                f"Claim Details:\n"
                f"- Claimant: {claim.get('claimant_name')}\n"
                f"- Incident Type: {claim.get('incident_type')}\n"
                f"- Claim Amount: ${claim.get('claim_amount'):,.2f}\n"
                f"- Days since policy start: {claim.get('days_since_policy_start', 'N/A')}\n"
                f"- Prior Claims Count: {claim.get('prior_claims_count', 0)}\n"
                f"- ML Fraud Probability Score: {ml_score:.2%} ({ml_score:.3f})\n"
                f"- Key SHAP Risk Drivers: {factors_str}\n\n"
                f"Provide a direct, plain-English summary for an insurance adjuster explaining why this claim was assigned this score and what specific risk indicators led to the decision."
            )
            
            completion = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a concise, objective insurance fraud analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq narrative generation failed/fallback: {e}")

    # Fallback plain English summary
    risk_level = "High" if ml_score > 0.8 else "Moderate" if ml_score >= 0.2 else "Low"
    summary = f"Claim flagged with {risk_level} risk score of {ml_score:.1%}. "
    if top_factors:
        drivers = [f["label"] for f in top_factors]
        summary += f"Primary risk drivers identified: {', '.join(drivers)}. "
    summary += f"Claim amount of ${claim.get('claim_amount', 0):,.2f} evaluated relative to policy tenure and claimant history."
    return summary
