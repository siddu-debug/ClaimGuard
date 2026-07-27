import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    claim_id = Column(String, unique=True, index=True, nullable=False)
    policy_id = Column(String, index=True, nullable=False)
    claimant_name = Column(String, nullable=False)
    policy_start_date = Column(String, nullable=False)
    claim_date = Column(String, nullable=False)
    claim_amount = Column(Float, nullable=False)
    incident_type = Column(String, nullable=False)
    incident_description = Column(Text, nullable=True)
    prior_claims_count = Column(Integer, default=0)
    
    # ML & Decision Outputs
    fraud_score = Column(Float, nullable=True)
    decision = Column(String, nullable=True)  # auto_approve, auto_reject, manual_review
    status = Column(String, nullable=False, default="pending") # auto_approve, auto_reject, manual_review, approved, rejected
    explanation = Column(Text, nullable=True)
    shap_values = Column(JSON, nullable=True)
    raw_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    policy_id = Column(String, unique=True, index=True, nullable=False)
    policy_start_date = Column(String, nullable=False)
    policy_holder = Column(String, nullable=False)
    coverage_limit = Column(Float, default=100000.0)

class ScoreLog(Base):
    __tablename__ = "score_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    claim_id = Column(String, nullable=False)
    fraud_score = Column(Float, nullable=False)
    decision = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
