"""
src/models/metrics.py
=====================
Métricas analíticas avanzadas para problemas con desbalance severo de clases.
Calcula PR-AUC, ROC-AUC, Lift@10, Lift@20 e Intervalos de Confianza (IC 95%)
mediante Stratified Bootstrap.
"""

from typing import Dict, Any, Tuple
import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    precision_recall_curve,
    auc,
    brier_score_loss
)


def calculate_lift_at_k(y_true: np.ndarray, y_prob: np.ndarray, k: float = 0.10) -> float:
    """
    Calcula el Lift al percentil k (ej. k=0.10 para Lift@10).
    Lift = (Precisión en el top k%) / (Prevalencia global de la clase positiva).
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)

    n_samples = len(y_true)
    n_positives = np.sum(y_true)

    if n_positives == 0 or n_samples == 0:
        return 0.0

    global_prevalence = n_positives / n_samples

    # Ordenar instancias de mayor a menor probabilidad predicha
    sorted_indices = np.argsort(y_prob)[::-1]
    cutoff = max(1, int(np.ceil(k * n_samples)))

    top_indices = sorted_indices[:cutoff]
    top_positives = np.sum(y_true[top_indices])

    precision_at_k = top_positives / cutoff
    lift = precision_at_k / global_prevalence

    return float(lift)


def evaluate_binary_predictions(y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
    """Evalúa las predicciones probabilísticas retornando el set completo de métricas."""
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)

    # ROC-AUC
    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5

    # PR-AUC (Precision-Recall AUC)
    try:
        precision, recall, _ = precision_recall_curve(y_true, y_prob)
        pr_auc = float(auc(recall, precision))
    except Exception:
        pr_auc = 0.0

    # Lift@10 y Lift@20
    lift_10 = calculate_lift_at_k(y_true, y_prob, k=0.10)
    lift_20 = calculate_lift_at_k(y_true, y_prob, k=0.20)

    # Brier Score (calibración)
    brier = float(brier_score_loss(y_true, y_prob))

    return {
        "pr_auc": round(pr_auc, 4),
        "lift_at_10": round(lift_10, 3),
        "lift_at_20": round(lift_20, 3),
        "roc_auc": round(roc_auc, 4),
        "brier_score": round(brier, 4)
    }


def stratified_bootstrap_ci(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bootstraps: int = 1000,
    alpha: float = 0.05,
    random_state: int = 42
) -> Dict[str, Dict[str, float]]:
    """
    Calcula Intervalos de Confianza empíricos al (1 - alpha)% mediante Stratified Bootstrap.
    Garantiza remuestreo preservando la proporción exacta de la clase minoritaria.
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)

    rng = np.random.RandomState(random_state)
    pos_idx = np.where(y_true == 1)[0]
    neg_idx = np.where(y_true == 0)[0]

    n_pos = len(pos_idx)
    n_neg = len(neg_idx)

    boot_metrics = {
        "pr_auc": [],
        "lift_at_10": [],
        "lift_at_20": [],
        "roc_auc": []
    }

    for _ in range(n_bootstraps):
        sample_pos = rng.choice(pos_idx, size=n_pos, replace=True)
        sample_neg = rng.choice(neg_idx, size=n_neg, replace=True)
        boot_idx = np.concatenate([sample_pos, sample_neg])

        y_t_boot = y_true[boot_idx]
        y_p_boot = y_prob[boot_idx]

        metrics = evaluate_binary_predictions(y_t_boot, y_p_boot)
        for m in boot_metrics:
            boot_metrics[m].append(metrics[m])

    ci_results = {}
    lower_pct = 100 * (alpha / 2)
    upper_pct = 100 * (1 - alpha / 2)

    for m, vals in boot_metrics.items():
        arr = np.array(vals)
        ci_results[m] = {
            "mean": round(float(np.mean(arr)), 4),
            "std": round(float(np.std(arr)), 4),
            "ci_lower": round(float(np.percentile(arr, lower_pct)), 4),
            "ci_upper": round(float(np.percentile(arr, upper_pct)), 4)
        }

    return ci_results
