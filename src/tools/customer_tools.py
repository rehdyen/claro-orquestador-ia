"""
src/tools/customer_tools.py
===========================
Herramientas analíticas para el Customer Intelligence Agent:
- Puntuación probabilística con Modelos A y B
- Asignación rigurosa de deciles poblacionales
- Detección de patrones de riesgo (SILENT_CHURN_PATTERN, CRITICAL_BOTH, etc.)
- Explicabilidad local con SHAP TreeExplainer
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

import joblib
import numpy as np
import pandas as pd
import shap

# Umbrales poblacionales calculados sobre Development Set
CHURN_DEC_CUTOFFS = [0.0355, 0.0089, 0.0035, 0.0017, 0.0010, 0.0005, 0.0003, 0.0001, 0.0]
INTENT_DEC_CUTOFFS = [0.7526, 0.5848, 0.4862, 0.4055, 0.3343, 0.2679, 0.2083, 0.1479, 0.0899]
ARPU_P75_COP = 109840.25


def _get_decile(prob: float, cutoffs: List[float]) -> int:
    """Asigna el decil (1 = Top 10% más riesgoso, 10 = Menor riesgo)."""
    for decile_idx, cutoff in enumerate(cutoffs, start=1):
        if prob >= cutoff:
            return decile_idx
    return 10


class CustomerIntelligenceTools:
    def __init__(self):
        models_dir = Path("outputs/models")
        self.model_a = joblib.load(models_dir / "model_a_churn.joblib")
        self.model_b = joblib.load(models_dir / "model_b_intencion.joblib")
        self.explainer_a = shap.TreeExplainer(self.model_a)
        self.explainer_b = shap.TreeExplainer(self.model_b)

        # Cargar lista de predictoras
        audit = pd.read_csv("docs/feature_audit.csv")
        self.predictors = audit[audit["feature_role"] == "PREDICTOR"]["variable"].tolist()

    def score_customer(self, customer_record: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula scores de riesgo, deciles de población y clasifica el patrón de riesgo."""
        # Convertir a DataFrame asegurando orden de columnas
        df_row = pd.DataFrame([customer_record])
        for col in self.predictors:
            if col not in df_row.columns:
                df_row[col] = np.nan
        df_row = df_row[self.predictors].copy()

        # Inferencia
        churn_prob = float(self.model_a.predict_proba(df_row)[0, 1])
        intent_prob = float(self.model_b.predict_proba(df_row)[0, 1])

        churn_decile = _get_decile(churn_prob, CHURN_DEC_CUTOFFS)
        intent_decile = _get_decile(intent_prob, INTENT_DEC_CUTOFFS)

        arpu = float(customer_record.get("VAL_RENTA_ACTUAL", 0.0))
        is_high_value = arpu >= ARPU_P75_COP

        # Clasificación del Patrón de Riesgo
        if churn_decile == 1 and intent_decile >= 6:
            risk_pattern = "SILENT_CHURN_PATTERN"
        elif churn_decile <= 2 and intent_decile <= 2:
            risk_pattern = "CRITICAL_BOTH"
        elif churn_decile <= 2 and intent_decile > 2:
            risk_pattern = "CHURN_DOMINANT"
        elif churn_decile > 2 and intent_decile <= 2:
            risk_pattern = "INTENT_DOMINANT"
        elif churn_decile in [3, 4, 5] or intent_decile in [3, 4, 5]:
            risk_pattern = "MODERATE"
        else:
            risk_pattern = "LOW"

        # Calcular SHAP local
        shap_a = self.explainer_a.shap_values(df_row)
        vals_a = shap_a[1] if isinstance(shap_a, list) else shap_a
        vals_a = vals_a[0] if len(vals_a.shape) > 1 else vals_a

        top_indices = np.argsort(np.abs(vals_a))[::-1][:5]
        top_drivers = [
            {"feature": self.predictors[idx], "shap_value": round(float(vals_a[idx]), 4)}
            for idx in top_indices
        ]

        return {
            "churn_score": round(churn_prob, 4),
            "churn_decile": churn_decile,
            "intention_score": round(intent_prob, 4),
            "intention_decile": intent_decile,
            "arpu": round(arpu, 2),
            "is_high_value": is_high_value,
            "risk_pattern": risk_pattern,
            "top_drivers": top_drivers
        }

    def get_cluster_profile(self) -> Dict[str, Any]:
        """Retorna el perfil consolidado del Cluster 3."""
        return {
            "cluster_id": 3,
            "total_clients": 20000,
            "churn_rate_pct": 0.52,
            "intention_rate_pct": 19.91,
            "mean_arpu_cop": 96446.78,
            "arpu_p75_cop": ARPU_P75_COP,
            "primary_churn_drivers": [
                "VAL_RECLAMOS_MES",
                "VELOCIDAD_INTERNET_MBPS",
                "VAL_RENTA_ACTUAL",
                "VAL_VAR_RENTA"
            ]
        }
