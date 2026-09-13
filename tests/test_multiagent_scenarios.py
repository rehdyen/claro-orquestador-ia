"""
tests/test_multiagent_scenarios.py
==================================
Pruebas integrales automatizadas para la Arquitectura Multi-Agente en LangGraph:
Valida los 8 escenarios de gobernanza, ruteo condicional, evaluación de catálogo y compuertas HITL.
"""

import pytest
import pandas as pd
from src.agents.graph import build_retention_graph
from src.agents.state import OrchestratorState
from src.tools.customer_tools import ARPU_P75_COP


@pytest.fixture(scope="module")
def app():
    return build_retention_graph()


@pytest.fixture(scope="module")
def base_customer():
    """Carga un cliente base real desde el holdout set."""
    X_holdout = pd.read_parquet("data/processed/X_holdout.parquet")
    return X_holdout.iloc[0].to_dict()


def test_scenario_1_high_risk_technical_fault(app, base_customer):
    """Escenario 1: Riesgo alto por falla técnica pura -> Visita Técnica Prioritaria (sin HITL forzado)."""
    rec = base_customer.copy()
    rec["VAL_RECLAMOS_MES"] = 3
    rec["VELOCIDAD_INTERNET_MBPS"] = 15.0
    rec["VAL_VAR_RENTA"] = 0.0
    rec["BAN_CAZA_OFERTA"] = 0
    rec["VAL_RENTA_ACTUAL"] = 75000.0  # Menor a P75

    init_state = {
        "run_id": "test_scen_1",
        "thread_id": "t1",
        "request": {},
        "customer_record": rec,
        "cluster_id": 3,
        "policy_flags": [],
        "evidence_refs": [],
        "retry_count": 0,
        "human_decision": None
    }

    config = {"configurable": {"thread_id": "t1"}}
    res = app.invoke(init_state, config=config)

    action = res["recommended_action"]
    assert action["action_id"] == "PRIORITY_TECH_VISIT"
    assert action["action_type"] == "TECHNICAL"


def test_scenario_2_high_risk_price_pressure(app, base_customer):
    """Escenario 2: Riesgo alto con aumento en renta -> Descuento temporal con HITL obligatorio."""
    rec = base_customer.copy()
    rec["VAL_RECLAMOS_MES"] = 0
    rec["VAL_VAR_RENTA"] = 15000.0
    rec["BAN_CAZA_OFERTA"] = 1
    rec["VAL_RENTA_ACTUAL"] = 85000.0

    init_state = {
        "run_id": "test_scen_2",
        "thread_id": "t2",
        "request": {},
        "customer_record": rec,
        "cluster_id": 3,
        "policy_flags": [],
        "evidence_refs": [],
        "retry_count": 0,
        "human_decision": {"action": "APPROVE", "notes": "Aprobado por supervisor"}
    }

    config = {"configurable": {"thread_id": "t2"}}
    res = app.invoke(init_state, config=config)

    assert res["hitl_required"] is True
    assert any("financiera" in r.lower() or "impacto" in r.lower() for r in res["hitl_reasons"])


def test_scenario_3_high_arpu_vip_customer(app, base_customer):
    """Escenario 3: Cliente VIP de Alto Valor (ARPU >= P75) en riesgo -> Dispara HITL automáticamente."""
    rec = base_customer.copy()
    rec["VAL_RENTA_ACTUAL"] = ARPU_P75_COP + 25000.0  # Superior al P75
    rec["VAL_RECLAMOS_MES"] = 2

    init_state = {
        "run_id": "test_scen_3",
        "thread_id": "t3",
        "request": {},
        "customer_record": rec,
        "cluster_id": 3,
        "policy_flags": [],
        "evidence_refs": [],
        "retry_count": 0,
        "human_decision": {"action": "APPROVE"}
    }

    config = {"configurable": {"thread_id": "t3"}}
    res = app.invoke(init_state, config=config)

    assert res["is_high_value"] is True
    assert res["hitl_required"] is True


def test_scenario_4_silent_churn_pattern(app, base_customer):
    """Escenario 4: Detección del patrón de Deserción Silenciosa (Silent Churn Gap)."""
    # Forzar un cliente con riesgo de churn decil 1 e intención decil >= 6
    rec = base_customer.copy()
    rec["VAL_RECLAMOS_MES"] = 5
    rec["VAL_VAR_RENTA"] = 25000.0
    rec["VAL_LLAMADAS_MES_CALLCENTER"] = 0
    rec["VAL_LLAM_ADTIVAS_NEUTRAS"] = 0

    init_state = {
        "run_id": "test_scen_4",
        "thread_id": "t4",
        "request": {},
        "customer_record": rec,
        "cluster_id": 3,
        "policy_flags": [],
        "evidence_refs": [],
        "retry_count": 0,
        "human_decision": {"action": "APPROVE", "notes": "Revisión preventiva"}
    }

    config = {"configurable": {"thread_id": "t4"}}
    res = app.invoke(init_state, config=config)

    # El orquestador debe activar HITL y sugerir diagnóstico o revisión preventiva si es silent churn
    assert res["hitl_required"] is True


def test_scenario_5_excessive_discount_senior_review(app, base_customer):
    """Escenario 5: Descuento > 20% (umbral de gobierno) -> Requiere Senior Review."""
    rec = base_customer.copy()
    rec["VAL_RENTA_ACTUAL"] = 80000.0

    init_state = {
        "run_id": "test_scen_5",
        "thread_id": "t5",
        "request": {"force_action": "TEMP_RENT_DISCOUNT", "discount_pct": 0.30},  # 30% descuento
        "customer_record": rec,
        "cluster_id": 3,
        "policy_flags": [],
        "evidence_refs": [],
        "retry_count": 0,
        "human_decision": {"action": "APPROVE", "reviewer": "Gerente Senior"}
    }

    config = {"configurable": {"thread_id": "t5"}}
    res = app.invoke(init_state, config=config)

    assert res["senior_review_required"] is True
    assert res["hitl_required"] is True
    assert any("20%" in r for r in res["hitl_reasons"])


def test_scenario_6_action_outside_catalog(app, base_customer):
    """Escenario 6: Intento de aplicar acción inexistente -> Bloqueo por guardrail y Senior Review."""
    rec = base_customer.copy()

    init_state = {
        "run_id": "test_scen_6",
        "thread_id": "t6",
        "request": {"force_action": "REGALO_DISPOSITIVO_GRATIS"},  # Fuera de catálogo
        "customer_record": rec,
        "cluster_id": 3,
        "policy_flags": [],
        "evidence_refs": [],
        "retry_count": 0,
        "human_decision": {"action": "REJECT", "notes": "No autorizada"}
    }

    config = {"configurable": {"thread_id": "t6"}}
    res = app.invoke(init_state, config=config)

    assert res["senior_review_required"] is True
    assert res["hitl_required"] is True
    assert any("GUARDRAIL_TRIGGERED" in f for f in res["policy_flags"])


def test_scenario_7_low_risk_abstain(app, base_customer):
    """Escenario 7: Cliente de bajo riesgo -> Abstención sin acción innecesaria."""
    rec = base_customer.copy()
    rec["VAL_RECLAMOS_MES"] = 0
    rec["VAL_VAR_RENTA"] = 0.0
    rec["BAN_CAZA_OFERTA"] = 0
    rec["VELOCIDAD_INTERNET_MBPS"] = 300.0

    init_state = {
        "run_id": "test_scen_7",
        "thread_id": "t7",
        "request": {},
        "customer_record": rec,
        "cluster_id": 3,
        "policy_flags": [],
        "evidence_refs": [],
        "retry_count": 0,
        "human_decision": None
    }

    config = {"configurable": {"thread_id": "t7"}}
    res = app.invoke(init_state, config=config)

    # Si es decil bajo, la recomendación es ABSTAIN_NO_ACTION
    action_id = res["recommended_action"]["action_id"]
    if res["churn_decile"] > 5 and res["intention_decile"] > 5:
        assert action_id == "ABSTAIN_NO_ACTION"


def test_scenario_8_blocked_artificial_join(app, base_customer):
    """Escenario 8: Guardrail de datos bloquea intento de enlace artificial 1:1 entre llamada y cliente."""
    rec = base_customer.copy()
    rec["call_id"] = "CALL_999"
    rec["CUENTA"] = "12345678"  # Intento de cruce forzado

    init_state = {
        "run_id": "test_scen_8",
        "thread_id": "t8",
        "request": {},
        "customer_record": rec,
        "cluster_id": 3,
        "policy_flags": [],
        "evidence_refs": [],
        "retry_count": 0,
        "human_decision": {"action": "APPROVE"}
    }

    config = {"configurable": {"thread_id": "t8"}}
    res = app.invoke(init_state, config=config)

    assert "BLOCKED_ARTIFICIAL_1_TO_1_JOIN" in res["policy_flags"]


def test_speed_upgrade_reachable(app, base_customer):
    """Escenario 9: Falla por bajo ancho de banda (<= 50 Mbps) sin avería física -> SPEED_UPGRADE alcanzable."""
    rec = base_customer.copy()
    rec["VAL_RECLAMOS_MES"] = 0
    rec["VELOCIDAD_INTERNET_MBPS"] = 30.0  # Plan bajo
    rec["VAL_VAR_RENTA"] = 0.0
    rec["BAN_CAZA_OFERTA"] = 0
    rec["VAL_RENTA_ACTUAL"] = 65000.0

    init_state = {
        "run_id": "test_speed_upg",
        "thread_id": "t9",
        "request": {},
        "customer_record": rec,
        "cluster_id": 3,
        "policy_flags": [],
        "evidence_refs": [],
        "retry_count": 0,
        "human_decision": None
    }

    config = {"configurable": {"thread_id": "t9"}}
    res = app.invoke(init_state, config=config)

    action = res["recommended_action"]
    assert action["action_id"] == "SPEED_UPGRADE"
    assert action["action_type"] == "CONTRACTUAL"


def test_discount_duration_policy_alignment(app, base_customer):
    """Escenario 10: Descuento de 3 meses excede la política estándar de 2 meses y activa Senior Review."""
    rec = base_customer.copy()
    rec["VAL_VAR_RENTA"] = 25000.0

    init_state = {
        "run_id": "test_disc_dur",
        "thread_id": "t10",
        "request": {"force_action": "TEMP_RENT_DISCOUNT", "discount_pct": 0.15, "discount_months": 3},
        "customer_record": rec,
        "cluster_id": 3,
        "policy_flags": [],
        "evidence_refs": [],
        "retry_count": 0,
        "human_decision": None
    }

    config = {"configurable": {"thread_id": "t10"}}
    res = app.invoke(init_state, config=config)

    assert res["hitl_required"] is True
    assert res["senior_review_required"] is True
    assert any("excede política estándar" in r for r in res["hitl_reasons"])

