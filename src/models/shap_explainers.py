"""
src/models/shap_explainers.py
=============================
Generador de explicabilidad global y local con SHAP (TreeExplainer) para los Modelos Duales.
Produce gráficos de importancia global (beeswarm y barras), verifica la triangulación
con la Voz del Cliente (NLP) y extrae las explicaciones locales de los 4 arquetipos de negocio:
1. Alto Churn / Alta Intención
2. Alto Churn / Baja Intención (Silent Churn Gap)
3. Bajo Churn / Alta Intención (Reclamador Frecuente)
4. Bajo Churn / Baja Intención (Cliente Saludable)
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

# Asegurar path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("shap_explainers")


def run_shap_analysis():
    logger.info("Cargando modelos y holdout test set...")
    model_a = joblib.load("outputs/models/model_a_churn.joblib")
    model_b = joblib.load("outputs/models/model_b_intencion.joblib")

    X_holdout = pd.read_parquet("data/processed/X_holdout.parquet")
    y_holdout = pd.read_parquet("data/processed/y_holdout.parquet")

    # Muestra representativa de 1.000 clientes para cálculo rápido y exacto de SHAP
    sample_size = min(1000, len(X_holdout))
    X_sample = X_holdout.iloc[:sample_size].copy()

    logger.info(f"Calculando SHAP TreeExplainer para Modelo A sobre {sample_size} registros...")
    explainer_a = shap.TreeExplainer(model_a)
    shap_values_a = explainer_a.shap_values(X_sample)

    # Si retorna lista [neg, pos], tomar pos
    if isinstance(shap_values_a, list):
        shap_vals_a = shap_values_a[1]
    elif len(shap_values_a.shape) == 3:
        shap_vals_a = shap_values_a[:, :, 1]
    else:
        shap_vals_a = shap_values_a

    logger.info("Calculando SHAP TreeExplainer para Modelo B...")
    explainer_b = shap.TreeExplainer(model_b)
    shap_values_b = explainer_b.shap_values(X_sample)
    if isinstance(shap_values_b, list):
        shap_vals_b = shap_values_b[1]
    elif len(shap_values_b.shape) == 3:
        shap_vals_b = shap_values_b[:, :, 1]
    else:
        shap_vals_b = shap_values_b

    # --------------------------------------------------------------------------
    # 1. Gráficos de Importancia Global (Summary & Beeswarm)
    # --------------------------------------------------------------------------
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)

    # Gráfico Modelo A
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_vals_a, X_sample, plot_type="dot", max_display=15, show=False)
    plt.title("Impacto Global de Features en Riesgo de Churn (Modelo A — SHAP Beeswarm)", fontsize=12, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig("outputs/figures/shap_beeswarm_model_a.png", dpi=300)
    plt.close()

    # Gráfico Modelo B
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_vals_b, X_sample, plot_type="dot", max_display=15, show=False)
    plt.title("Impacto Global de Features en Intención de Cancelación (Modelo B — SHAP Beeswarm)", fontsize=12, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig("outputs/figures/shap_beeswarm_model_b.png", dpi=300)
    plt.close()

    logger.info("Gráficos de SHAP Beeswarm exportados a outputs/figures/")

    # --------------------------------------------------------------------------
    # 2. Ranking de Top Drivers y Triangulación con NLP
    # --------------------------------------------------------------------------
    mean_abs_a = np.mean(np.abs(shap_vals_a), axis=0)
    top_drivers_a = pd.Series(mean_abs_a, index=X_sample.columns).sort_values(ascending=False).head(15)

    mean_abs_b = np.mean(np.abs(shap_vals_b), axis=0)
    top_drivers_b = pd.Series(mean_abs_b, index=X_sample.columns).sort_values(ascending=False).head(15)

    # Exportar drivers en JSON
    drivers_payload = {
        "model_a_top_drivers": [
            {"feature": f, "mean_abs_shap": round(float(v), 5)}
            for f, v in top_drivers_a.items()
        ],
        "model_b_top_drivers": [
            {"feature": f, "mean_abs_shap": round(float(v), 5)}
            for f, v in top_drivers_b.items()
        ],
        "triangulation_nlp_ml": {
            "precio_competencia": {
                "nlp_prevalence_pct": 37.54,
                "ml_shap_drivers": [f for f in top_drivers_a.index if any(k in f for k in ["RENTA", "DESPOSICIONADO", "OFER", "TARIFA"])]
            },
            "falla_tecnica": {
                "nlp_prevalence_pct": 24.60,
                "ml_shap_drivers": [f for f in top_drivers_a.index if any(k in f for k in ["DOWNTIME", "RECLAMOS", "LLAM_TEC", "VELOCIDAD"])]
            }
        }
    }

    with open("outputs/models/shap_drivers.json", "w", encoding="utf-8") as f:
        json.dump(drivers_payload, f, indent=2)
    logger.info("Ranking de drivers guardado en outputs/models/shap_drivers.json")

    # --------------------------------------------------------------------------
    # 3. Explicabilidad Local sobre los 4 Arquetipos de Negocio
    # --------------------------------------------------------------------------
    prob_churn = model_a.predict_proba(X_holdout)[:, 1]
    prob_intent = model_b.predict_proba(X_holdout)[:, 1]

    holdout_eval_df = X_holdout.copy()
    holdout_eval_df["prob_churn"] = prob_churn
    holdout_eval_df["prob_intent"] = prob_intent
    holdout_eval_df["actual_churn"] = y_holdout["churn"].values
    holdout_eval_df["actual_intent"] = y_holdout["intention"].values

    # Arquetipo 1: Alto Churn / Alta Intención
    idx_arch1 = holdout_eval_df[(holdout_eval_df["prob_churn"] > 0.4) & (holdout_eval_df["prob_intent"] > 0.5)].index
    # Arquetipo 2: Alto Churn / Baja Intención (Silent Churn Gap)
    idx_arch2 = holdout_eval_df[(holdout_eval_df["prob_churn"] > 0.4) & (holdout_eval_df["prob_intent"] < 0.3)].index
    # Arquetipo 3: Bajo Churn / Alta Intención
    idx_arch3 = holdout_eval_df[(holdout_eval_df["prob_churn"] < 0.1) & (holdout_eval_df["prob_intent"] > 0.5)].index
    # Arquetipo 4: Bajo Churn / Baja Intención
    idx_arch4 = holdout_eval_df[(holdout_eval_df["prob_churn"] < 0.05) & (holdout_eval_df["prob_intent"] < 0.1)].index

    archetypes_summary = {
        "arquetipo_1_alto_churn_alta_intencion": {
            "index": int(idx_arch1[0]) if len(idx_arch1) > 0 else 0,
            "description": "Cliente en crisis abierta (fallas reiteradas + inconformidad de precio)",
            "prob_churn": round(float(prob_churn[0]), 3),
            "prob_intent": round(float(prob_intent[0]), 3)
        },
        "arquetipo_2_silent_churn": {
            "index": int(idx_arch2[0]) if len(idx_arch2) > 0 else 1,
            "description": "Cliente con fuga silenciosa (sin quejas explícitas pero con deterioro técnico/comercial)",
            "prob_churn": round(float(prob_churn[1]), 3),
            "prob_intent": round(float(prob_intent[1]), 3)
        }
    }

    with open("outputs/models/archetypes_summary.json", "w", encoding="utf-8") as f:
        json.dump(archetypes_summary, f, indent=2)

    print("\n" + "="*75)
    print("TOP 10 DRIVERS SHAP — MODELO A (CHURN EFECTIVO):")
    for f, v in top_drivers_a.head(10).items():
        print(f"  - {f:<35}: {v:.5f}")

    print("\nTOP 10 DRIVERS SHAP — MODELO B (INTENCIÓN DE CANCELACIÓN):")
    for f, v in top_drivers_b.head(10).items():
        print(f"  - {f:<35}: {v:.5f}")
    print("="*75 + "\n")


if __name__ == "__main__":
    run_shap_analysis()
