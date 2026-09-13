"""
tests/test_models.py
====================
Pruebas unitarias automatizadas para los modelos predictivos duales (LightGBM)
y métricas de evaluación (PR-AUC, Lift@10, Bootstrap).
"""

import json
from pathlib import Path
import pytest
import joblib
import numpy as np
import pandas as pd

from src.models.metrics import calculate_lift_at_k, evaluate_binary_predictions


@pytest.fixture
def model_a():
    return joblib.load("outputs/models/model_a_churn.joblib")


@pytest.fixture
def model_b():
    return joblib.load("outputs/models/model_b_intencion.joblib")


@pytest.fixture
def sample_data():
    X_holdout = pd.read_parquet("data/processed/X_holdout.parquet")
    return X_holdout.head(10)


def test_models_exist():
    """Verifica que ambos modelos serializados existan en disco."""
    assert Path("outputs/models/model_a_churn.joblib").exists()
    assert Path("outputs/models/model_b_intencion.joblib").exists()
    assert Path("outputs/models/metricas_modelos.json").exists()


def test_model_a_predictions(model_a, sample_data):
    """Verifica que el Modelo A genere probabilidades válidas [0, 1]."""
    probs = model_a.predict_proba(sample_data)[:, 1]
    assert len(probs) == len(sample_data)
    assert np.all(probs >= 0.0)
    assert np.all(probs <= 1.0)


def test_model_b_predictions(model_b, sample_data):
    """Verifica que el Modelo B genere probabilidades válidas [0, 1]."""
    probs = model_b.predict_proba(sample_data)[:, 1]
    assert len(probs) == len(sample_data)
    assert np.all(probs >= 0.0)
    assert np.all(probs <= 1.0)


def test_lift_at_10_calculation():
    """Verifica el cálculo matemático exacto de Lift@10 en caso sintético."""
    # 100 muestras, 10 positivos (10% base prevalence)
    y_true = np.array([1]*10 + [0]*90)
    # Si las 10 probabilidades más altas tienen los 10 positivos, Precision@10 = 1.0 -> Lift = 1.0 / 0.10 = 10.0x
    y_prob = np.array([0.95]*10 + [0.10]*90)
    lift_10 = calculate_lift_at_k(y_true, y_prob, k=0.10)
    assert pytest.approx(lift_10, 0.01) == 10.0


def test_metrics_json_integrity():
    """Verifica que el archivo de métricas contenga todos los campos exigidos."""
    with open("outputs/models/metricas_modelos.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)

    assert "model_a_churn" in metrics
    assert "model_b_intencion" in metrics
    assert "holdout_bootstrap_ci95" in metrics["model_a_churn"]
    assert "lift_at_10" in metrics["model_a_churn"]["holdout_point_estimates"]
    assert metrics["model_a_churn"]["holdout_point_estimates"]["lift_at_10"] >= 5.0
