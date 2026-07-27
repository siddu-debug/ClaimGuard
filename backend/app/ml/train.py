import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve, auc, confusion_matrix, classification_report
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import shap

from app.ml.features import extract_features_dataframe, FEATURE_COLUMNS
from data.generate_synthetic_claims import generate_synthetic_dataset

def load_or_create_data(base_dir: Path) -> pd.DataFrame:
    raw_dir = base_dir / "data" / "raw"
    os.makedirs(raw_dir, exist_ok=True)
    
    # Check if any external Kaggle CSV exists in raw_dir
    csv_files = [f for f in raw_dir.glob("*.csv") if f.name != "synthetic_claims.csv"]
    if csv_files:
        raw_csv = csv_files[0]
        print(f"Loading external dataset from {raw_csv}...")
        df = pd.read_csv(raw_csv)
        # Verify required columns exist or map them
        if "is_fraud" in df.columns:
            return df
            
    synthetic_csv = raw_dir / "synthetic_claims.csv"
    if not synthetic_csv.exists():
        print("Generating synthetic claims dataset...")
        df = generate_synthetic_dataset(num_records=2500, output_path=str(synthetic_csv))
    else:
        print(f"Loading synthetic claims from {synthetic_csv}...")
        df = pd.read_csv(synthetic_csv)
        
    return df

def train_fraud_model():
    base_dir = Path(__file__).resolve().parent.parent.parent
    models_dir = base_dir / "models"
    os.makedirs(models_dir, exist_ok=True)
    
    df = load_or_create_data(base_dir)
    
    # Feature extraction
    X = extract_features_dataframe(df)
    y = df["is_fraud"].values
    
    print(f"Dataset shape: {X.shape}, Fraud cases: {np.sum(y)} / {len(y)} ({np.mean(y)*100:.2f}%)")
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Handle imbalanced data with SMOTE on training set
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    
    print(f"After SMOTE training set size: {X_train_res.shape}, Positive labels: {np.sum(y_train_res)}")
    
    # Train XGBoost Classifier
    model = XGBClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss"
    )
    model.fit(X_train_res, y_train_res)
    
    # Predictions & Probabilities
    y_probs = model.predict_proba(X_test)[:, 1]
    
    # Compute Precision-Recall Curve & PR-AUC
    precision, recall, thresholds = precision_recall_curve(y_test, y_probs)
    pr_auc = float(auc(recall, precision))
    
    # Recall at Precision >= 0.80
    recall_at_p80 = 0.0
    for p, r in zip(precision, recall):
        if p >= 0.80:
            recall_at_p80 = max(recall_at_p80, float(r))
            
    # Confusion matrix at 0.5 threshold
    y_pred = (y_probs >= 0.5).astype(int)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    print("\n--- MODEL EVALUATION ---")
    print(f"PR-AUC Score: {pr_auc:.4f}")
    print(f"Recall at Precision >= 0.80: {recall_at_p80:.4f}")
    print("Confusion Matrix (0.5 threshold):")
    print(np.array(cm))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # SHAP Explainer
    explainer = shap.TreeExplainer(model)
    
    # Save Model Artifacts
    artifact = {
        "model": model,
        "explainer": explainer,
        "feature_names": FEATURE_COLUMNS,
        "model_version": "1.0.0"
    }
    
    model_path = models_dir / "fraud_model.pkl"
    joblib.dump(artifact, model_path)
    print(f"\nModel artifact saved to {model_path}")
    
    # Save Metrics JSON
    metrics = {
        "pr_auc": round(pr_auc, 4),
        "recall_at_p80": round(recall_at_p80, 4),
        "confusion_matrix": cm,
        "training_sample_count": len(df),
        "feature_names": FEATURE_COLUMNS,
        "model_version": "1.0.0"
    }
    
    metrics_path = models_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {metrics_path}")

if __name__ == "__main__":
    train_fraud_model()
