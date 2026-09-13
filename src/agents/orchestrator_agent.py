"""
src/agents/orchestrator_agent.py
================================
Retention Orchestrator Agent:
Consolida la evidencia estructurada y no estructurada, evalúa el catálogo de acciones,
calcula el impacto económico financiero (ARPU salvado vs costo) y aplica la política
estricta de Human-in-the-Loop (HITL) recomendada por la dirección analítica.
"""

from typing import Dict, Any, List
from src.agents.state import OrchestratorState
from src.tools.catalog_tools import ACTION_CATALOG, estimate_economic_impact


def retention_orchestrator_node(state: OrchestratorState) -> Dict[str, Any]:
    """Nodo decisor comercial y financiero del orquestador."""
    customer = state.get("customer_record", {})
    risk_pattern = state.get("risk_pattern", "LOW")
    churn_decile = state.get("churn_decile", 10)
    intent_decile = state.get("intention_decile", 10)
    churn_score = state.get("churn_score", 0.0)
    arpu = state.get("arpu", 0.0)
    is_high_value = state.get("is_high_value", False)
    top_drivers = state.get("top_drivers", [])
    driver_names = [d["feature"] for d in top_drivers]

    # Banderas objetivas de fricción
    has_tech_fault = (
        customer.get("VAL_RECLAMOS_MES", 0) >= 1 or
        customer.get("VELOCIDAD_INTERNET_MBPS", 100) < 50 or
        any("RECLAMOS" in d or "DOWNTIME" in d for d in driver_names)
    )
    # Presión de precio: variación positiva en renta o cliente caza-ofertas
    has_price_pressure = (
        customer.get("VAL_VAR_RENTA", 0) > 0 or
        customer.get("BAN_CAZA_OFERTA", 0) == 1 or
        any("VAR_RENTA" in d for d in driver_names)
    )

    # --------------------------------------------------------------------------
    # 1. Selección Racional de Acción según Evidencia Dominante
    # --------------------------------------------------------------------------
    discount_pct = 0.0
    discount_months = 0

    if risk_pattern == "SILENT_CHURN_PATTERN":
        # Churn alto pero sin reclamos explícitos -> Diagnóstico preventivo
        selected_action_id = "PREVENTIVE_DIAGNOSTIC"

    elif customer.get("VELOCIDAD_INTERNET_MBPS", 100) <= 50 and customer.get("VAL_RECLAMOS_MES", 0) == 0 and not has_price_pressure:
        # Lentitud por bajo ancho de banda (plan <= 50 Mbps) sin avería física -> Upgrade de velocidad FTTH
        selected_action_id = "SPEED_UPGRADE"

    elif has_tech_fault and not has_price_pressure:
        # Falla técnica / avería física de red (reclamos activos) -> Visita técnica prioritaria
        selected_action_id = "PRIORITY_TECH_VISIT"

    elif has_price_pressure:
        # Presión de precio -> Descuento temporal
        selected_action_id = "TEMP_RENT_DISCOUNT"
        discount_pct = 0.15  # 15% (dentro del límite de gobierno <= 20%)
        discount_months = 2

    elif customer.get("BAN_CAZA_OFERTA", 0) == 1:
        # Caza ofertas -> Bono de fidelización (paquete premium)
        selected_action_id = "LOYALTY_BONUS"
        discount_months = 3

    elif churn_decile <= 3 or intent_decile <= 3:
        # Riesgo alto genérico -> Descuento temporal moderado
        selected_action_id = "TEMP_RENT_DISCOUNT"
        discount_pct = 0.10
        discount_months = 2
    else:
        # Riesgo bajo -> Abstenerse
        selected_action_id = "ABSTAIN_NO_ACTION"

    # Verificar si una solicitud forzó una acción específica
    forced_action = state.get("request", {}).get("force_action")
    if forced_action:
        selected_action_id = forced_action
        discount_pct = state.get("request", {}).get("discount_pct", discount_pct)
        discount_months = state.get("request", {}).get("discount_months", discount_months)

    action_meta = ACTION_CATALOG.get(selected_action_id)
    action_dict = action_meta.model_dump() if action_meta else {
        "action_id": selected_action_id,
        "action_name": "Acción No Catalogada",
        "action_type": "UNKNOWN",
        "cost_cop": 0.0,
        "requires_hitl": True
    }

    # --------------------------------------------------------------------------
    # 2. Evaluación Económica Financiera
    # --------------------------------------------------------------------------
    econ = estimate_economic_impact(
        arpu_cop=arpu,
        churn_prob=churn_score,
        churn_decile=churn_decile,
        action_id=selected_action_id,
        discount_pct=discount_pct,
        discount_months=discount_months,
        uplift_scenario="base"
    )

    # --------------------------------------------------------------------------
    # 3. Política Rigurosa de Human-in-the-Loop (HITL Governance)
    # --------------------------------------------------------------------------
    hitl_reasons: List[str] = []
    senior_review = False

    # Regla 1: Acción financiera (toca dinero/tarifa)
    if selected_action_id in ["TEMP_RENT_DISCOUNT", "LOYALTY_BONUS"]:
        hitl_reasons.append("Acción comercial/financiera con impacto en facturación.")

    # Regla 2: Acción contractual (modifica producto)
    if selected_action_id in ["SPEED_UPGRADE"]:
        hitl_reasons.append("Modificación contractual de servicio (Upgrade de velocidad).")

    # Regla 3: Cliente de Alto Valor (ARPU >= P75) en decil crítico
    if is_high_value and (churn_decile <= 2 or intent_decile <= 2):
        hitl_reasons.append(f"Cliente VIP de Alto Valor (ARPU ${arpu:,.0f} >= P75) en Decil Crítico {min(churn_decile, intent_decile)}.")

    # Regla 4: Silent Churn Pattern
    if risk_pattern == "SILENT_CHURN_PATTERN":
        hitl_reasons.append("Patrón de Deserción Silenciosa (Decil Churn 1 sin intención previa registrada).")

    # Regla 5: Descuento Alto (> 20% umbral configurable de gobierno)
    if discount_pct > 0.20:
        hitl_reasons.append(f"Descuento solicitado ({discount_pct*100:.0f}%) supera el umbral de gobierno del 20%.")
        senior_review = True

    # Regla 6: Duración extendida de descuento (> 2 meses)
    if discount_months > 2 and selected_action_id == "TEMP_RENT_DISCOUNT":
        hitl_reasons.append(f"Duración de descuento ({discount_months} meses) excede política estándar.")
        senior_review = True

    # Regla 7: Acción fuera de catálogo
    if selected_action_id not in ACTION_CATALOG:
        hitl_reasons.append(f"Acción '{selected_action_id}' no pertenece al catálogo oficial.")
        senior_review = True

    # Regla 8: Flags de política preexistentes
    if state.get("policy_flags"):
        hitl_reasons.extend(state.get("policy_flags"))

    hitl_required = len(hitl_reasons) > 0

    return {
        "recommended_action": action_dict,
        "action_cost": econ.get("intervention_cost_total", 0.0),
        "discount_pct": discount_pct,
        "discount_duration_months": discount_months,
        "economic_impact": econ,
        "hitl_required": hitl_required,
        "senior_review_required": senior_review,
        "hitl_reasons": hitl_reasons
    }
