# AI-Powered Insurance Claims Automation Platform (ClaimGuard AI)

A full-stack, portfolio-ready platform featuring machine learning for fraud risk scoring, SHAP explainability, and Groq LLM integration for structured field extraction and plain-English narrative risk summaries.

## System Architecture

```
                                    +----------------------------------+
                                    |        React + Vite SPA          |
                                    |    Dashboard & Claims Detail     |
                                    +----------------+-----------------+
                                                     | (REST API)
                                                     v
                                    +----------------------------------+
                                    |           FastAPI App            |
                                    +----------------+-----------------+
                                                     |
            +----------------------------------------+---------------------------------------+
            |                                        |                                       |
            v                                        v                                       v
+-----------------------+                +-----------------------+               +-----------------------+
|  Rules Engine (Layer) |                |   XGBoost Classifier  |               |    Groq LLM Client    |
|   - Amount Thresholds |                |   - SMOTE balanced    |               |    - JSON Extraction  |
|   - Score Bounds      |                |   - SHAP explanation  |               |    - Narrative Summary|
+-----------+-----------+                +-----------+-----------+               +-----------+-----------+
            |                                        |                                       |
            +----------------------------------------+---------------------------------------+
                                                     |
                                                     v
                                        +--------------------------+
                                        |     SQLite Database      |
                                        +--------------------------+
```

## Tech Stack
* **Backend:** Python 3.11, FastAPI, Uvicorn, SQLAlchemy (SQLite dev db)
* **Machine Learning:** XGBoost Classifier, SHAP Explainability, scikit-learn, imbalanced-learn (SMOTE)
* **LLM Integration:** Groq SDK (`llama-3.3-70b-versatile`)
* **Frontend:** React, Vite, Tailwind CSS, Lucide icons

---

## Getting Started Locally

### 1. Pre-requisites
* Python 3.11+
* Node.js v18+

### 2. Backend Setup
1. Change directory to backend:
   ```bash
   cd backend
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment:
   Copy `.env.example` to `.env` and add your Groq API key:
   ```env
   GROQ_API_KEY=your-gsk-key-here
   DATABASE_URL=sqlite:///./claims.db
   ALLOWED_ORIGINS=http://localhost:5173
   ```
5. Generate synthetic claims & train the ML model:
   ```bash
   python app/ml/train.py
   ```
   *Note: This will train the model, output confusion matrix evaluations/metrics, and save the model artifacts under `models/`.*
6. Start the FastAPI development server:
   ```bash
   python app/main.py
   ```

### 3. Frontend Setup
1. Change directory to frontend:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Configure environment:
   Create `.env` file:
   ```env
   VITE_API_URL=http://localhost:8000
   ```
4. Start the Vite development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## Running Backend Tests
Execute standard unit and integration tests (tests are written using mocks for the Groq client to prevent API costs during testing):
```bash
cd backend
pytest -v
```

---

## Deployment Instructions

### 1. Backend Deployment (Render)
This repository is configured for automated container-based web service deployments on Render.
1. Create a new **Web Service** on Render and link this repository.
2. Select **Docker** as the Runtime environment. Render will automatically detect `render.yaml` and the `backend/Dockerfile` configured.
3. In the environment variables settings page, configure:
   * `GROQ_API_KEY`: Your official Groq API token.
   * `DATABASE_URL`: `sqlite:///./claims.db` (or provision a Render PostgreSQL instance and use the connection string).
   * `ALLOWED_ORIGINS`: Your deployed Vercel frontend URL.

### 2. Frontend Deployment (Vercel)
1. Import the repository in Vercel.
2. Set the root directory to `frontend/`.
3. In the Environment Variables settings, configure:
   * `VITE_API_URL`: Your deployed Render Web Service backend URL.
   * Vercel will automatically apply the routing rules defined in `vercel.json` to handle SPA routing rewrites.
