import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if available
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "Insurance Claims Automation Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = ""
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./claims.db")
    
    ALLOWED_ORIGINS: list = [
        origin.strip() for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
        ).split(",") if origin.strip()
    ]
    
    # Path settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MODEL_PATH: Path = BASE_DIR / "models" / "fraud_model.pkl"
    METRICS_PATH: Path = BASE_DIR / "models" / "metrics.json"

settings = Settings()
