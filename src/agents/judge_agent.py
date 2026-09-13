"""
src/agents/judge_agent.py
=========================
Módulo de Evaluación y Juez Automatizado (Judge Node):
Evalúa la recomendación del Orquestador bajo criterios objetivos:
- Groundedness: Coherencia entre causa raíz de fricción y acción seleccionada.
- Adherencia al Catálogo: La acción existe en ACTION_CATALOG.
- Control de Descuento: Respeta límites comerciales autorizados (<= 20%).
- Manejo de Reintentos: Permite máximo 1 retry antes de escalar a revisión humana.
"""

from typing import Dict, Any
from src.agents.state import OrchestratorState
from src.tools.catalog_tools import ACTION_CATALOG


def judge_agent_node(state: OrchestratorState) -> Dict[str, Any]:
    """Nodo evaluador de calidad y seguridad de decisión."""
    rec_action = state.get("recommended_action", {})
    action_id = rec_action.get("action_id", "UNKNOWN")
    discount_pct = state.get("discount_pct", 0.0)
    customer = state.get("customer_record", {})
    retry_count = state.get("retry_count", 0)

    scores = {
        "catalog_adherence": 5 if action_id in ACTION_CATALOG else 1,
        "groundedness": 5,
        "governance_compliance": 5
    }
    critique_notes = []

    # 1. Regla de Coherencia Causa-Acción
    has_tech_fault_only = (
        customer.get("VAL_RECLAMOS_MES", 0) >= 1 and
        customer.get("VAL_VAR_RENTA", 0) <= 0 and
        customer.get("BAN_CAZA_OFERTA", 0) == 0
    )
    if has_tech_fault_only and action_id == "TEMP_RENT_DISCOUNT":
        scores["groundedness"] = 2
        critique_notes.append("Inconsistencia: Se recomendó descuento comercial a un cliente con falla técnica pura.")

    # 2. Regla de Límite de Descuento
    if discount_pct > 0.20 and not state.get("senior_review_required", False):
        scores["governance_compliance"] = 2
        critique_notes.append("Violación de gobierno: Descuento supera el 20% sin bandera de Senior Review.")

    # Calificación global
    min_score = min(scores.values())
    judge_passed = min_score >= 4

    # Gestión de reintentos
    new_retry_count = retry_count
    if not judge_passed:
        new_retry_count += 1

    return {
        "judge_scores": scores,
        "judge_passed": judge_passed,
        "retry_count": new_retry_count,
        "policy_flags": critique_notes
    }
