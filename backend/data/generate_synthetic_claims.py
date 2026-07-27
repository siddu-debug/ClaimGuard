import os
import random
import datetime
from pathlib import Path
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

INCIDENT_TYPES = ["auto_collision", "water_damage", "theft_burglary", "fire_damage", "slip_and_fall", "hail_damage"]

DESCRIPTIONS = {
    "auto_collision": [
        "Vehicle hit from behind at an intersection.",
        "Side collision while changing lanes on highway.",
        "Single-vehicle crash into guardrail due to rain.",
        "Parked vehicle struck overnight in residential lot."
    ],
    "water_damage": [
        "Burst plumbing pipe under kitchen sink causing hardwood damage.",
        "Roof leak after thunderstorm damaging ceiling and plaster.",
        "Washing machine supply hose ruptured in basement.",
        "Water heater leakage flooded ground floor utility room."
    ],
    "theft_burglary": [
        "Forced entry through rear door; electronics and jewelry stolen.",
        "Vehicle broken into overnight; personal belongings taken.",
        "Bicycle and power tools stolen from detached garage.",
        "Storefront window smashed; inventory taken from display."
    ],
    "fire_damage": [
        "Kitchen grease fire damaged cabinets and ventilation hood.",
        "Electrical short in bedroom outlet ignited curtains.",
        "Outdoor grill fire scorched deck and rear siding.",
        "Space heater malfunction caused smoke damage throughout upstairs."
    ],
    "slip_and_fall": [
        "Customer slipped on wet floor near entrance with no warning sign.",
        "Guest tripped on uneven walkway flagstone during evening event.",
        "Visitor fell on icy front porch steps.",
        "Delivery person tripped over loose carpeting in hallway."
    ],
    "hail_damage": [
        "Severe hailstorm damaged roof shingles and outdoor AC unit.",
        "Hail dented vehicle hood, roof, and cracked windshield.",
        "Hail ruined patio furniture and damaged vinyl siding.",
        "Storm pelted commercial roof membrane causing leaks."
    ]
}

def generate_synthetic_dataset(num_records: int = 2000, output_path: str = None) -> pd.DataFrame:
    records = []
    
    start_range = datetime.date(2022, 1, 1)
    end_range = datetime.date(2024, 6, 1)
    
    for i in range(1, num_records + 1):
        claim_id = f"CLM-{100000 + i}"
        policy_id = f"POL-{random.randint(10000, 99999)}"
        claimant_name = fake.name()
        
        # Policy start date
        policy_start = fake.date_between(start_date=start_range, end_date=end_range)
        
        # Claim date (after policy start date)
        # Fraud risk feature: days between policy start and claim date
        days_gap = random.choices(
            [random.randint(1, 15), random.randint(16, 90), random.randint(91, 730)],
            weights=[0.10, 0.25, 0.65]
        )[0]
        
        claim_date = policy_start + datetime.timedelta(days=days_gap)
        
        incident_type = random.choice(INCIDENT_TYPES)
        incident_description = random.choice(DESCRIPTIONS[incident_type])
        
        # Prior claims count
        prior_claims_count = random.choices([0, 1, 2, 3, 4, 5], weights=[0.60, 0.22, 0.10, 0.05, 0.02, 0.01])[0]
        
        # Claim amount distribution
        if incident_type in ["fire_damage", "water_damage"]:
            claim_amount = round(random.lognormvariate(9.2, 0.8), 2)  # Higher average (~$10k-$60k)
        else:
            claim_amount = round(random.lognormvariate(8.2, 0.7), 2)  # Medium average (~$3k-$20k)
            
        claim_amount = max(500.0, min(claim_amount, 120000.0))
        
        # Fraud probability logic (~5% target total positive rate)
        # Correlated with short gap, high amount, and repeat prior claims
        fraud_prob = 0.01  # baseline
        
        if days_gap <= 14:
            fraud_prob += 0.35
        elif days_gap <= 45:
            fraud_prob += 0.10
            
        if claim_amount > 45000:
            fraud_prob += 0.25
        elif claim_amount > 25000:
            fraud_prob += 0.10
            
        if prior_claims_count >= 3:
            fraud_prob += 0.30
        elif prior_claims_count >= 2:
            fraud_prob += 0.10
            
        if incident_type == "fire_damage" and claim_amount > 50000:
            fraud_prob += 0.15
            
        is_fraud = 1 if random.random() < fraud_prob else 0
        
        records.append({
            "claim_id": claim_id,
            "policy_id": policy_id,
            "claimant_name": claimant_name,
            "policy_start_date": policy_start.strftime("%Y-%m-%d"),
            "claim_date": claim_date.strftime("%Y-%m-%d"),
            "claim_amount": claim_amount,
            "incident_type": incident_type,
            "incident_description": incident_description,
            "prior_claims_count": prior_claims_count,
            "is_fraud": is_fraud
        })
        
    df = pd.DataFrame(records)
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Generated {len(df)} synthetic claims saved to {output_path}")
        print(f"Fraud distribution: {df['is_fraud'].value_counts(normalize=True).to_dict()}")
        
    return df

if __name__ == "__main__":
    raw_dir = Path(__file__).resolve().parent / "raw"
    target_csv = raw_dir / "synthetic_claims.csv"
    generate_synthetic_dataset(num_records=2000, output_path=str(target_csv))
