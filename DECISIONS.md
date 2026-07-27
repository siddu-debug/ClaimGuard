# Architecture & Engineering Decisions Log (DECISIONS.md)

This log records major architectural decisions, model choices, and implementation approaches chosen for the Insurance Claims Automation Platform.

---

## 1. Machine Learning Stack & Strategy
### Decision: XGBoost + SMOTE + SHAP
* **Rationale:** Insurance fraud datasets are inherently imbalanced (typically ~5% or fewer positive cases). We chose **SMOTE (Synthetic Minority Over-sampling Technique)** to balance the class distribution on the training partition before feeding it into **XGBoost**.
* **Model Choice:** XGBoost was selected because of its high training efficiency, robustness against overfitting when hyperparameters (like `max_depth` and learning rates) are tuned, and native support for tree-based feature explanations.
* **Explainability:** We utilized **SHAP (SHapley Additive exPlanations) TreeExplainer** instead of simple feature importances. This computes localized feature attribution weights for each specific claim. The UI shows these contributions as interactive positive (risk-increasing) and negative (risk-decreasing) bars, providing auditability for claim adjusters.

---

## 2. LLM Orchestration & Resilience
### Decision: Groq API (`llama-3.3-70b-versatile`) with Resilient Fallback Layer
* **Model:** We used `llama-3.3-70b-versatile` due to its high context throughput, speed, and capability to follow strict JSON schema extraction prompts.
* **Extraction Resilience:** For unstructured claim narratives, the Groq API extracts key fields into structured JSON. If the API key is missing or the service is down, the code falls back to an internal **regex-based heuristic parser** to prevent service disruption.
* **Explanation Resilience:** The narrative explanation combining SHAP features and claims details falls back to a formatted templated string explanation if the LLM cannot be reached.

---

## 3. Database Layer
### Decision: SQLite via SQLAlchemy (PostgreSQL Ready)
* **Rationale:** For local development and easy deployment on free-tier systems without complex database configurations, SQLite (`claims.db`) is ideal. Using SQLAlchemy allows the database URL connection string to be easily swapped for **PostgreSQL** in production with zero code changes.

---

## 4. Frontend & Deployment Framework
### Decision: React + Vite + Tailwind CSS (SPA)
* **Rationale:** A full Single Page Application built on React/Vite allows for fluid transitions, micro-animations, and client-side page switching. Vercel hosting handles the static assets with rewrites (`vercel.json`) while Render hosts the Dockerized FastAPI backend.
* **CORS & Environment:** To ensure absolute decoupling, the frontend relies on `VITE_API_URL` to communicate with the backend, allowing them to be hosted on entirely different subdomains/domains.
