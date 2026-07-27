from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import init_db, SessionLocal
from app.db.models import Claim
from app.api import claims, scoring

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema on startup
    init_db()
    
    # Pre-seed sample synthetic claims if database is empty
    db = SessionLocal()
    try:
        if db.query(Claim).count() == 0:
            print("Database empty. Seeding initial synthetic claims...")
            from data.generate_synthetic_claims import generate_synthetic_dataset
            from app.schemas.claim import ClaimCreateStructured
            from app.api.claims import create_claim
            
            df = generate_synthetic_dataset(num_records=20)
            for _, row in df.iterrows():
                claim_in = ClaimCreateStructured(
                    claim_id=row["claim_id"],
                    policy_id=row["policy_id"],
                    claimant_name=row["claimant_name"],
                    policy_start_date=str(row["policy_start_date"]),
                    claim_date=str(row["claim_date"]),
                    claim_amount=float(row["claim_amount"]),
                    incident_type=str(row["incident_type"]),
                    incident_description=str(row["incident_description"]),
                    prior_claims_count=int(row["prior_claims_count"])
                )
                create_claim(claim_in, db)
            print("Database successfully seeded with 20 initial claims!")
    except Exception as e:
        print(f"Error seeding initial database claims: {e}")
    finally:
        db.close()
        
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for seamless portfolio demo deployment (Vercel + local)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(claims.router)
app.include_router(scoring.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": settings.VERSION}

@app.get("/", tags=["Root"])
def root_endpoint():
    return {
        "message": "Insurance Claims Automation Platform API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
