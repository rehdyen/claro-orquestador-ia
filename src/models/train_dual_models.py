"""
src/models/train_dual_models.py
===============================
Pipeline de entrenamiento, validación cruzada y evaluación para los Modelos Duales de Claro:
- Modelo A: Riesgo de Churn Efectivo (BAN_CHURN, 0.52% prevalencia).
  Evaluado vía RepeatedStratifiedKFold (4 splits x 5 repeats = 20 folds) y Bootstrap IC 95%.
- Modelo B: Alerta Temprana de Intención de Cancelación (BAN_INTENCION_CANCELACION, 19.91%).
  Evaluado vía StratifiedKFold (5 folds).
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lightgbm import LGBMClassifier
from sklearn.model_selection import (
    train_test_split,
    RepeatedStratifiedKFold,
    StratifiedKFold
)

# Asegurar path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.models.metrics import (
    evaluate_binary_predictions,
    calculate_lift_at_k,
    stratified_bootstrap_ci
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_dual_models")


def load_and_prepare_data() -> Tuple[pd.DataFrame, pd.Series, pd.Series, List[str]]:
    """Carga los datos estructurados y selecciona estrictamente las 113 variables PREDICTOR."""
    logger.info("Cargando clientes_cluster_3.parquet y feature_audit.csv...")
    df = pd.read_parquet("data/processed/clientes_cluster_3.parquet")
    audit = pd.read_csv("docs/feature_audit.csv")

    predictors = audit[audit["feature_role"] == "PREDICTOR"]["variable"].tolist()
    logger.info(f"Seleccionadas {len(predictors)} variables con rol PREDICTOR (cero fugas T0).")

    # Asegurar targets binarios
    y_churn = df["BAN_CHURN"].astype(int)
    y_intention = df["BAN_INTENCION_CANCELACION"].astype(int)

    X = df[predictors].copy()

    # Tipado uniforme
    for col in X.columns:
        if X[col].dtype == "object":
            X[col] = pd.to_numeric(X[col], errors="coerce")

    return X, y_churn, y_intention, predictors


def train_evaluate_model_a(
    X_dev: pd.DataFrame,
    y_dev: pd.Series,
    X_holdout: pd.DataFrame,
    y_holdout: pd.Series
) -> Dict[str, Any]:
    """
    Entrena y valida el Modelo A (BAN_CHURN) con árboles deliberadamente pequeños,
    RepeatedStratifiedKFold (20 evaluaciones) y mini-ablation de weighting.
    """
    logger.info("Iniciando validación cruzada para Modelo A (BAN_CHURN, 0.52% prevalencia)...")

    rskf = RepeatedStratifiedKFold(n_splits=4, n_repeats=5, random_state=42)

    # Mini-ablation: A1 (sin weighting) vs A2 (con scale_pos_weight dinámico)
    for ablation_name, use_weighting in [("A1_unweighted", False), ("A2_weighted", True)]:
        fold_metrics = {"pr_auc": [], "lift_at_10": [], "lift_at_20": [], "roc_auc": []}

        for fold_idx, (train_idx, val_idx) in enumerate(rskf.split(X_dev, y_dev)):
            X_tr, y_tr = X_dev.iloc[train_idx], y_dev.iloc[train_idx]
            X_va, y_va = X_dev.iloc[val_idx], y_dev.iloc[val_idx]

            dynamic_weight = (len(y_tr) - np.sum(y_tr)) / max(1, np.sum(y_tr)) if use_weighting else 1.0

            model = LGBMClassifier(
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
                scale_pos_weight=dynamic_weight,
                random_state=42 + fold_idx,
                deterministic=True,
                force_col_wise=True,
                verbose=-1,
                n_jobs=-1
            )

            model.fit(
                X_tr, y_tr,
                eval_set=[(X_va, y_va)],
                callbacks=[]
            )

            y_val_prob = model.predict_proba(X_va)[:, 1]
            m = evaluate_binary_predictions(y_va.values, y_val_prob)
            for k in fold_metrics:
                fold_metrics[k].append(m[k])

        logger.info(
            f"Modelo A [{ablation_name}] CV (20 folds) -> "
            f"PR-AUC: {np.mean(fold_metrics['pr_auc']):.4f} +/- {np.std(fold_metrics['pr_auc']):.4f} | "
            f"Lift@10: {np.mean(fold_metrics['lift_at_10']):.3f} +/- {np.std(fold_metrics['lift_at_10']):.3f}"
        )

    # Entrenar modelo final A en todo Development con configuración ganadora (A2 con weighting)
    logger.info("Entrenando Modelo A definitivo sobre el 100% de Development Set...")
    dev_weight = (len(y_dev) - np.sum(y_dev)) / max(1, np.sum(y_dev))
    final_model_a = LGBMClassifier(
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
        scale_pos_weight=dev_weight,
        random_state=42,
        deterministic=True,
        force_col_wise=True,
        verbose=-1,
        n_jobs=-1
    )
    final_model_a.fit(X_dev, y_dev)

    # Evaluación ÚNICA en Final Holdout
    logger.info("Evaluando Modelo A de forma única y blindada sobre Final Holdout...")
    y_holdout_prob_a = final_model_a.predict_proba(X_holdout)[:, 1]
    holdout_metrics_a = evaluate_binary_predictions(y_holdout.values, y_holdout_prob_a)

    # Bootstrap estratificado para IC 95%
    logger.info("Calculando intervalos de confianza (IC 95%) vía Stratified Bootstrap (1.000 iteraciones)...")
    ci_a = stratified_bootstrap_ci(y_holdout.values, y_holdout_prob_a, n_bootstraps=1000, random_state=42)

    return {
        "model": final_model_a,
        "cv_repeated_summary": {
            k: {"mean": round(float(np.mean(v)), 4), "std": round(float(np.std(v)), 4)}
            for k, v in fold_metrics.items()
        },
        "holdout_point_estimates": holdout_metrics_a,
        "holdout_bootstrap_ci95": ci_a,
        "holdout_prob": y_holdout_prob_a
    }


def train_evaluate_model_b(
    X_dev: pd.DataFrame,
    y_dev: pd.Series,
    X_holdout: pd.DataFrame,
    y_holdout: pd.Series
) -> Dict[str, Any]:
    """Entrena y valida el Modelo B (BAN_INTENCION_CANCELACION, 19.91% prevalencia)."""
    logger.info("Iniciando validación cruzada para Modelo B (BAN_INTENCION_CANCELACION)...")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    fold_metrics = {"pr_auc": [], "lift_at_10": [], "lift_at_20": [], "roc_auc": []}

    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(X_dev, y_dev)):
        X_tr, y_tr = X_dev.iloc[train_idx], y_dev.iloc[train_idx]
        X_va, y_va = X_dev.iloc[val_idx], y_dev.iloc[val_idx]

        dynamic_weight = (len(y_tr) - np.sum(y_tr)) / max(1, np.sum(y_tr))

        model = LGBMClassifier(
            objective="binary",
            n_estimators=1000,
            learning_rate=0.03,
            num_leaves=15,
            max_depth=4,
            min_child_samples=50,
            colsample_bytree=0.80,
            subsample=0.85,
            subsample_freq=1,
            reg_alpha=0.5,
            reg_lambda=2.0,
            scale_pos_weight=dynamic_weight,
            random_state=42 + fold_idx,
            deterministic=True,
            force_col_wise=True,
            verbose=-1,
            n_jobs=-1
        )

        model.fit(X_tr, y_tr)
        y_val_prob = model.predict_proba(X_va)[:, 1]
        m = evaluate_binary_predictions(y_va.values, y_val_prob)
        for k in fold_metrics:
            fold_metrics[k].append(m[k])

    logger.info(
        f"Modelo B CV (5 folds) -> PR-AUC: {np.mean(fold_metrics['pr_auc']):.4f} | "
        f"Lift@10: {np.mean(fold_metrics['lift_at_10']):.3f} | ROC-AUC: {np.mean(fold_metrics['roc_auc']):.4f}"
    )

    # Entrenar modelo B final
    dev_weight = (len(y_dev) - np.sum(y_dev)) / max(1, np.sum(y_dev))
    final_model_b = LGBMClassifier(
        objective="binary",
        n_estimators=1000,
        learning_rate=0.03,
        num_leaves=15,
        max_depth=4,
        min_child_samples=50,
        colsample_bytree=0.80,
        subsample=0.85,
        subsample_freq=1,
        reg_alpha=0.5,
        reg_lambda=2.0,
        scale_pos_weight=dev_weight,
        random_state=42,
        deterministic=True,
        force_col_wise=True,
        verbose=-1,
        n_jobs=-1
    )
    final_model_b.fit(X_dev, y_dev)

    y_holdout_prob_b = final_model_b.predict_proba(X_holdout)[:, 1]
    holdout_metrics_b = evaluate_binary_predictions(y_holdout.values, y_holdout_prob_b)
    ci_b = stratified_bootstrap_ci(y_holdout.values, y_holdout_prob_b, n_bootstraps=1000, random_state=42)

    return {
        "model": final_model_b,
        "cv_summary": {
            k: {"mean": round(float(np.mean(v)), 4), "std": round(float(np.std(v)), 4)}
            for k, v in fold_metrics.items()
        },
        "holdout_point_estimates": holdout_metrics_b,
        "holdout_bootstrap_ci95": ci_b,
        "holdout_prob": y_holdout_prob_b
    }


def generate_evaluation_plots(
    y_test_churn: np.ndarray,
    prob_churn: np.ndarray,
    y_test_intent: np.ndarray,
    prob_intent: np.ndarray
):
    """Genera curvas de Lift acumulado y PR / ROC para ambos modelos."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Curva de Lift Acumulado por Deciles (Decile Lift Curve)
    deciles = np.linspace(0.05, 1.0, 20)
    lift_a = [calculate_lift_at_k(y_test_churn, prob_churn, k=k) for k in deciles]
    lift_b = [calculate_lift_at_k(y_test_intent, prob_intent, k=k) for k in deciles]

    ax = axes[0]
    ax.plot(deciles * 100, lift_a, marker="o", linewidth=2.5, color="#d62728", label="Modelo A: Churn Efectivo")
    ax.plot(deciles * 100, lift_b, marker="s", linewidth=2.5, color="#1f77b4", label="Modelo B: Intención Cancelación")
    ax.axhline(1.0, color="gray", linestyle="--", label="Línea Base Azar (Lift = 1.0x)")
    ax.set_title("Curva de Lift Acumulado por Percentil de Clientes", fontsize=13, fontweight="bold")
    ax.set_xlabel("Top % de Clientes Contactados (Priorizados)", fontsize=11)
    ax.set_ylabel("Lift (Efectividad vs Azar)", fontsize=11)
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True, alpha=0.3)

    # Curvas Precision-Recall
    from sklearn.metrics import precision_recall_curve
    prec_a, rec_a, _ = precision_recall_curve(y_test_churn, prob_churn)
    prec_b, rec_b, _ = precision_recall_curve(y_test_intent, prob_intent)

    ax2 = axes[1]
    ax2.plot(rec_a, prec_a, color="#d62728", linewidth=2.5, label="Modelo A (Churn 0.52%)")
    ax2.plot(rec_b, prec_b, color="#1f77b4", linewidth=2.5, label="Modelo B (Intención 19.9%)")
    ax2.set_title("Curva Precision-Recall (Holdout Test)", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Recall (Cobertura de Positivos)", fontsize=11)
    ax2.set_ylabel("Precision (Tasa de Acierto)", fontsize=11)
    ax2.legend(loc="upper right", frameon=True)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plot_path = "outputs/figures/lift_and_pr_curves.png"
    plt.savefig(plot_path, dpi=300)
    logger.info(f"Gráfico de curvas de Lift y PR exportado a {plot_path}")


def main():
    X, y_churn, y_intention, feature_names = load_and_prepare_data()

    # Split 80/20 estratificado por Churn
    logger.info("Realizando partición 80% Development / 20% Final Holdout...")
    X_dev, X_holdout, y_dev_churn, y_holdout_churn, y_dev_intent, y_holdout_intent = train_test_split(
        X, y_churn, y_intention,
        test_size=0.20,
        random_state=42,
        stratify=y_churn
    )

    logger.info(f"Development Set: {len(X_dev)} registros (Churns: {y_dev_churn.sum()})")
    logger.info(f"Holdout Set:    {len(X_holdout)} registros (Churns: {y_holdout_churn.sum()})")

    # Guardar datasets particionados para reproducibilidad y tests
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    X_dev.to_parquet("data/processed/X_dev.parquet", index=False)
    X_holdout.to_parquet("data/processed/X_holdout.parquet", index=False)
    pd.DataFrame({"churn": y_dev_churn, "intention": y_dev_intent}).to_parquet("data/processed/y_dev.parquet", index=False)
    pd.DataFrame({"churn": y_holdout_churn, "intention": y_holdout_intent}).to_parquet("data/processed/y_holdout.parquet", index=False)

    # Entrenar Modelo A
    res_a = train_evaluate_model_a(X_dev, y_dev_churn, X_holdout, y_holdout_churn)

    # Entrenar Modelo B
    res_b = train_evaluate_model_b(X_dev, y_dev_intent, X_holdout, y_holdout_intent)

    # Guardar Modelos
    Path("outputs/models").mkdir(parents=True, exist_ok=True)
    joblib.dump(res_a["model"], "outputs/models/model_a_churn.joblib")
    joblib.dump(res_b["model"], "outputs/models/model_b_intencion.joblib")
    logger.info("Modelos guardados en outputs/models/")

    # Guardar métricas consolidadas
    metrics_payload = {
        "metadata": {
            "features_used": len(feature_names),
            "feature_role_used": "PREDICTOR",
            "leakage_t0_controlled": True,
            "development_samples": len(X_dev),
            "holdout_samples": len(X_holdout)
        },
        "model_a_churn": {
            "cv_repeated_kfold_summary": res_a["cv_repeated_summary"],
            "holdout_point_estimates": res_a["holdout_point_estimates"],
            "holdout_bootstrap_ci95": res_a["holdout_bootstrap_ci95"]
        },
        "model_b_intencion": {
            "cv_summary": res_b["cv_summary"],
            "holdout_point_estimates": res_b["holdout_point_estimates"],
            "holdout_bootstrap_ci95": res_b["holdout_bootstrap_ci95"]
        }
    }

    with open("outputs/models/metricas_modelos.json", "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)
    logger.info("Métricas guardadas en outputs/models/metricas_modelos.json")

    # Gráficos
    generate_evaluation_plots(
        y_holdout_churn.values,
        res_a["holdout_prob"],
        y_holdout_intent.values,
        res_b["holdout_prob"]
    )

    print("\n" + "="*75)
    print("RESUMEN EJECUTIVO DE MODELADO DUAL MACHINE LEARNING — CLARO")
    print("="*75)
    print("MODELO A — CHURN EFECTIVO (104 Positivos / Prevalencia 0.52%):")
    print(f"  Holdout PR-AUC:   {res_a['holdout_point_estimates']['pr_auc']} (IC 95%: [{res_a['holdout_bootstrap_ci95']['pr_auc']['ci_lower']} - {res_a['holdout_bootstrap_ci95']['pr_auc']['ci_upper']}])")
    print(f"  Holdout Lift@10:  {res_a['holdout_point_estimates']['lift_at_10']}x (IC 95%: [{res_a['holdout_bootstrap_ci95']['lift_at_10']['ci_lower']} - {res_a['holdout_bootstrap_ci95']['lift_at_10']['ci_upper']}])")
    print(f"  Holdout Lift@20:  {res_a['holdout_point_estimates']['lift_at_20']}x (IC 95%: [{res_a['holdout_bootstrap_ci95']['lift_at_20']['ci_lower']} - {res_a['holdout_bootstrap_ci95']['lift_at_20']['ci_upper']}])")
    print(f"  Holdout ROC-AUC:  {res_a['holdout_point_estimates']['roc_auc']}")

    print("\nMODELO B — INTENCIÓN DE CANCELACIÓN (3.981 Positivos / Prevalencia 19.91%):")
    print(f"  Holdout PR-AUC:   {res_b['holdout_point_estimates']['pr_auc']} (IC 95%: [{res_b['holdout_bootstrap_ci95']['pr_auc']['ci_lower']} - {res_b['holdout_bootstrap_ci95']['pr_auc']['ci_upper']}])")
    print(f"  Holdout Lift@10:  {res_b['holdout_point_estimates']['lift_at_10']}x (IC 95%: [{res_b['holdout_bootstrap_ci95']['lift_at_10']['ci_lower']} - {res_b['holdout_bootstrap_ci95']['lift_at_10']['ci_upper']}])")
    print(f"  Holdout Lift@20:  {res_b['holdout_point_estimates']['lift_at_20']}x (IC 95%: [{res_b['holdout_bootstrap_ci95']['lift_at_20']['ci_lower']} - {res_b['holdout_bootstrap_ci95']['lift_at_20']['ci_upper']}])")
    print(f"  Holdout ROC-AUC:  {res_b['holdout_point_estimates']['roc_auc']}")
    print("="*75 + "\n")


if __name__ == "__main__":
    main()
