"""
tests/test_catalog_roi.py
=========================
Pruebas unitarias para el Catálogo de Acciones y el Módulo Financiero de ROI:
- Integridad de catálogo oficial
- Cálculo económico empírico por decil (evita sesgo scale_pos_weight)
- Sensibilidad a los 3 escenarios de retención incremental (10%, 20%, 30%)
- Proyección agregada a nivel de portafolio para Cluster 3 (20.000 clientes)
"""

import pytest
from src.tools.catalog_tools import (
    ACTION_CATALOG,
    get_catalog,
    estimate_economic_impact,
    project_cluster_portfolio_impact,
    EMPIRICAL_CHURN_RATES,
    UPLIFT_SCENARIOS
)


def test_catalog_structure_and_types():
    catalog = get_catalog()
    assert len(catalog) >= 6
    assert "PRIORITY_TECH_VISIT" in catalog
    assert "TEMP_RENT_DISCOUNT" in catalog
    assert "PREVENTIVE_DIAGNOSTIC" in catalog
    assert "ABSTAIN_NO_ACTION" in catalog

    for action_id, action in catalog.items():
        assert "cost_cop" in action
        assert "requires_hitl" in action
        assert action["cost_cop"] >= 0.0


def test_empirical_decile_roi_calculation():
    # Cliente representativo del Cluster 3: ARPU $96.447 COP
    arpu = 96446.78
    
    # Evaluación en Decil 1 (tasa empírica 5.19%) con Visita Técnica ($35.000 COP)
    res_base = estimate_economic_impact(
        arpu_cop=arpu,
        churn_decile=1,
        action_id="PRIORITY_TECH_VISIT",
        uplift_scenario="base"
    )

    assert res_base["rate_source"] == "Empirical Decile 1"
    assert res_base["effective_churn_rate"] == 0.0519
    assert res_base["uplift_applied_pct"] == 20.0
    
    # Verificación matemática exacta:
    # Ingreso anual = 96446.78 * 12 = 1,157,361.36
    # Pérdida prevenida esperada = 1,157,361.36 * 0.0519 * 0.20 = 12,013.41 COP
    expected_loss_prevented = round(arpu * 12 * 0.0519 * 0.20, 2)
    assert abs(res_base["expected_prevented_loss"] - expected_loss_prevented) < 1.0

    # Costo intervención = 35.000 COP
    assert res_base["intervention_cost_total"] == 35000.0
    
    # Sensibilidad a 3 escenarios presente
    scenarios = res_base["scenarios_breakdown"]
    assert "conservative" in scenarios
    assert "base" in scenarios
    assert "optimistic" in scenarios
    assert scenarios["conservative"]["uplift_pct"] == 10.0
    assert scenarios["base"]["uplift_pct"] == 20.0
    assert scenarios["optimistic"]["uplift_pct"] == 30.0


def test_portfolio_projection_aggregate():
    projection = project_cluster_portfolio_impact(
        total_population=20000,
        target_decile_pct=0.10,
        mean_arpu_cop=96446.78,
        empirical_churn_rate_decile1=0.0519,
        avg_intervention_cost_cop=28000.0
    )

    assert projection["cluster_total_clients"] == 20000
    assert projection["target_clients_decil_1"] == 2000
    assert projection["expected_churners_decil_1"] == pytest.approx(103.8, 0.1)

    scenarios = projection["scenarios"]
    # Escenario Conservador (10% de 103.8 = ~10.4 clientes)
    assert scenarios["conservative"]["retained_clients"] == pytest.approx(10.4, 0.1)
    # Escenario Base (20% de 103.8 = ~20.8 clientes)
    assert scenarios["base"]["retained_clients"] == pytest.approx(20.8, 0.1)
    # Escenario Optimista (30% de 103.8 = ~31.1 clientes)
    assert scenarios["optimistic"]["retained_clients"] == pytest.approx(31.1, 0.1)
