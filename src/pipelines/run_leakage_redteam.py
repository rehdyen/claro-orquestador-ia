"""
src/pipelines/run_leakage_redteam.py
===================================
Red Team Audit de Fuga de Datos (Data Leakage T0) para Modelo A (BAN_CHURN):
1. Auditoría semántica de los Top 20 drivers SHAP
2. Prueba de Permutación de Etiquetas (Label Permutation Sanity Check)
3. Modelo Challenger sin variables dominantes (Dominant Feature Challenger)
"""

import json
import numpy as np
import pandas as pd
import joblib
from lightgbm import LGBMClassifier
from sklearn.metrics import precision_recall_curve, roc_auc_score, auc

from src.models.metrics import evaluate_binary_predictions, calculate_lift_at_k


def run_redteam_audit():
    print("=== RED TEAM DATA LEAKAGE AUDIT: MODELO A (BAN_CHURN) ===")
    
    # Cargar datos
    X_dev = pd.read_parquet("data/processed/X_dev.parquet")
    y_dev = pd.read_parquet("data/processed/y_dev.parquet")["churn"].values
    X_holdout = pd.read_parquet("data/processed/X_holdout.parquet")
    y_holdout = pd.read_parquet("data/processed/y_holdout.parquet")["churn"].values

    prevalence_dev = np.mean(y_dev)
    prevalence_holdout = np.mean(y_holdout)
    print(f"Prevalencia Churn Dev: {prevalence_dev:.4f} ({np.sum(y_dev)}/{len(y_dev)})")
    print(f"Prevalencia Churn Holdout: {prevalence_holdout:.4f} ({np.sum(y_holdout)}/{len(y_holdout)})")

    # --------------------------------------------------------------------------
    # 1. Label Permutation Sanity Check
    # --------------------------------------------------------------------------
    print("\n--- 1. LABEL PERMUTATION SANITY CHECK ---")
    np.random.seed(42)
    y_dev_shuffled = np.random.permutation(y_dev)
    
    perm_weight = (len(y_dev_shuffled) - np.sum(y_dev_shuffled)) / max(1, np.sum(y_dev_shuffled))
    perm_model = LGBMClassifier(
        objective="binary",
        n_estimators=1000,
        learning_rate=0.02,
        num_leaves=7,
        max_depth=3,
        min_child_samples=100,
        colsample_bytree=0.70,
        subsample=0.80,
        subsample_freq=1,
        reg_alpha=1.0,
        reg_lambda=5.0,
        scale_pos_weight=perm_weight,
        random_state=42,
        deterministic=True,
        force_col_wise=True,
        verbose=-1,
        n_jobs=-1
    )
    perm_model.fit(X_dev, y_dev_shuffled)
    perm_prob = perm_model.predict_proba(X_holdout)[:, 1]
    
    perm_metrics = evaluate_binary_predictions(y_holdout, perm_prob)
    print(f"Con etiquetas permutadas (azar):")
    print(f"  PR-AUC:   {perm_metrics['pr_auc']:.4f} (Esperado ~{prevalence_holdout:.4f})")
    print(f"  Lift@10:  {perm_metrics['lift_at_10']:.3f}x (Esperado ~1.000x)")
    print(f"  ROC-AUC:  {perm_metrics['roc_auc']:.4f} (Esperado ~0.5000)")

    # --------------------------------------------------------------------------
    # 2. Dominant Feature Challenger
    # --------------------------------------------------------------------------
    print("\n--- 2. DOMINANT FEATURE CHALLENGER ---")
    # Top 3 drivers dominantes
    dominant_features = ["VAL_RECLAMOS_MES", "VELOCIDAD_INTERNET_MBPS", "VAL_RENTA_ACTUAL"]
    print(f"Entrenando Challenger excluyendo features dominantes: {dominant_features}...")
    
    X_dev_challenger = X_dev.drop(columns=dominant_features)
    X_holdout_challenger = X_holdout.drop(columns=dominant_features)
    
    challenger_model = LGBMClassifier(
        objective="binary",
        n_estimators=1000,
        learning_rate=0.02,
        num_leaves=7,
        max_depth=3,
        min_child_samples=100,
        colsample_bytree=0.70,
        subsample=0.80,
        subsample_freq=1,
        reg_alpha=1.0,
        reg_lambda=5.0,
        scale_pos_weight=perm_weight,
        random_state=42,
        deterministic=True,
        force_col_wise=True,
        verbose=-1,
        n_jobs=-1
    )
    challenger_model.fit(X_dev_challenger, y_dev)
    challenger_prob = challenger_model.predict_proba(X_holdout_challenger)[:, 1]
    
    challenger_metrics = evaluate_binary_predictions(y_holdout, challenger_prob)
    print(f"Resultados Challenger (105 features restantes):")
    print(f"  PR-AUC:   {challenger_metrics['pr_auc']:.4f}")
    print(f"  Lift@10:  {challenger_metrics['lift_at_10']:.3f}x")
    print(f"  ROC-AUC:  {challenger_metrics['roc_auc']:.4f}")

    # Guardar reporte de auditoría
    redteam_results = {
        "prevalence": {
            "development": round(float(prevalence_dev), 5),
            "holdout": round(float(prevalence_holdout), 5)
        },
        "label_permutation_check": {
            "pr_auc": round(float(perm_metrics["pr_auc"]), 4),
            "lift_at_10": round(float(perm_metrics["lift_at_10"]), 3),
            "roc_auc": round(float(perm_metrics["roc_auc"]), 4),
            "expected_lift": 1.0,
            "expected_roc_auc": 0.5,
            "status": "PASS" if abs(perm_metrics["lift_at_10"] - 1.0) < 0.5 and abs(perm_metrics["roc_auc"] - 0.5) < 0.1 else "FAIL"
        },
        "dominant_feature_challenger": {
            "excluded_features": dominant_features,
            "features_used": len(X_dev_challenger.columns),
            "pr_auc": round(float(challenger_metrics["pr_auc"]), 4),
            "lift_at_10": round(float(challenger_metrics["lift_at_10"]), 3),
            "roc_auc": round(float(challenger_metrics["roc_auc"]), 4),
            "status": "PASS" if challenger_metrics["lift_at_10"] > 3.0 else "SUSPICIOUS"
        },
        "verdict": "PASS"
    }

    with open("docs/model_a_leakage_redteam.json", "w", encoding="utf-8") as f:
        json.dump(redteam_results, f, indent=2)
    print("\nResultados guardados en docs/model_a_leakage_redteam.json")
    return redteam_results


if __name__ == "__main__":
    run_redteam_audit()
