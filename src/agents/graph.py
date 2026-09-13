"""
src/agents/graph.py
===================
Orquestador Multi-Agente definitivo construido con LangGraph (StateGraph).
Implementa la arquitectura formal exigida por Claro Colombia:
- Capa 1: Validación y separación paralela (Customer Intelligence + VoC Agent)
- Capa 2: Fusión de evidencia (Merge Evidence)
- Capa 3: Orquestador de Retención (Catálogo y ROI)
- Capa 4: Guardrails determinísticos y Juez con reintentos
- Capa 5: Compuerta de políticas de gobierno y Human-in-the-Loop (HITL) con interrupt()
"""

import uuid
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from src.agents.state import OrchestratorState
from src.agents.customer_agent import customer_agent_node
from src.agents.voc_agent import voc_agent_node
from src.agents.orchestrator_agent import retention_orchestrator_node
from src.agents.judge_agent import judge_agent_node
from src.tools.catalog_tools import ACTION_CATALOG


# ------------------------------------------------------------------------------
# 1. Nodos de Flujo y Procesamiento
# ------------------------------------------------------------------------------

def validate_request_node(state: OrchestratorState) -> Dict[str, Any]:
    """Valida la estructura de entrada y asegura identificadores de trazabilidad."""
    run_id = state.get("run_id") or str(uuid.uuid4())
    thread_id = state.get("thread_id") or f"thread_{run_id[:8]}"
    cluster_id = state.get("cluster_id", 3)
    record = state.get("customer_record", {})

    policy_flags = []
    if not record:
        policy_flags.append("EMPTY_RECORD_WARNING")

    # Guardrail crítico: Prohibir uniones artificiales cliente-llamada
    if "call_id" in record and ("CUENTA" in record or "DOCUMENTO" in record):
        policy_flags.append("BLOCKED_ARTIFICIAL_1_TO_1_JOIN")

    return {
        "run_id": run_id,
        "thread_id": thread_id,
        "cluster_id": cluster_id,
        "policy_flags": policy_flags,
        "evidence_refs": [f"Sesión iniciada: run_id={run_id}, cluster={cluster_id}"]
    }


def merge_evidence_node(state: OrchestratorState) -> Dict[str, Any]:
    """Fusiona el contexto estructurado de inteligencia de cliente con la Voz del Cliente."""
    return {
        "evidence_refs": ["Evidencia unificada de modelos estructurados y llamadas VoC."]
    }


def deterministic_guardrails_node(state: OrchestratorState) -> Dict[str, Any]:
    """Aplica controles determinísticos inviolables antes de someter al Juez."""
    rec = state.get("recommended_action", {})
    action_id = rec.get("action_id", "UNKNOWN")
    flags = []

    # Guardrail G-SEC-01: Validación contra catálogo
    if action_id not in ACTION_CATALOG:
        flags.append(f"GUARDRAIL_TRIGGERED: Acción {action_id} no autorizada en catálogo.")

    # Guardrail G-SEC-02: Control de descuento máximo absoluto (no permitir > 35% bajo ninguna circunstancia)
    if state.get("discount_pct", 0.0) > 0.35:
        flags.append("GUARDRAIL_TRIGGERED: Descuento supera el límite de seguridad del 35%.")

    return {"policy_flags": flags}


def policy_gate_node(state: OrchestratorState) -> Dict[str, Any]:
    """Evalúa si la decisión requiere intervención humana obligatoria (HITL)."""
    hitl_required = state.get("hitl_required", False)
    if not state.get("judge_passed", True):
        hitl_required = True

    return {"hitl_required": hitl_required}


def human_review_node(state: OrchestratorState) -> Dict[str, Any]:
    """
    Pausa la ejecución mediante interrupt() para solicitar aprobación humana,
    o procesa la decisión humana si ya fue provista en el resume.
    """
    human_dec = state.get("human_decision")

    # Si aún no hay decisión humana provista, pausar con interrupt()
    if not human_dec:
        payload_for_human = {
            "run_id": state.get("run_id"),
            "customer_arpu": state.get("arpu"),
            "risk_pattern": state.get("risk_pattern"),
            "churn_decile": state.get("churn_decile"),
            "recommended_action": state.get("recommended_action"),
            "discount_pct": state.get("discount_pct"),
            "hitl_reasons": state.get("hitl_reasons"),
            "senior_review_required": state.get("senior_review_required")
        }
        human_response = interrupt(payload_for_human)
        human_dec = human_response if isinstance(human_response, dict) else {"action": "APPROVE", "notes": str(human_response)}

    return {
        "human_decision": human_dec,
        "evidence_refs": [f"Decisión Humana registrada: {human_dec.get('action', 'APPROVE')}"]
    }


def final_validation_node(state: OrchestratorState) -> Dict[str, Any]:
    """Aplica la resolución humana a la recomendación final."""
    human_dec = state.get("human_decision", {})
    action = human_dec.get("action", "APPROVE")
    rec = state.get("recommended_action", {})

    if action == "REJECT":
        final_action = ACTION_CATALOG["ABSTAIN_NO_ACTION"].model_dump()
        final_notes = f"Acción rechazada por revisor humano: {human_dec.get('notes', 'Sin observaciones')}."
    elif action == "EDIT":
        final_action = rec
        final_notes = f"Acción editada por revisor: {human_dec.get('notes', 'Ajustada')}"
    else:
        final_action = rec
        final_notes = "Acción aprobada formalmente por compuerta HITL."

    return {
        "recommended_action": final_action,
        "evidence_refs": [final_notes]
    }


def finalize_node(state: OrchestratorState) -> Dict[str, Any]:
    """Compila el artefacto de salida final estandarizado y verificable."""
    final_output = {
        "session": {
            "run_id": state.get("run_id"),
            "thread_id": state.get("thread_id"),
            "cluster_id": state.get("cluster_id")
        },
        "customer_evaluation": {
            "arpu_cop": state.get("arpu"),
            "is_high_value": state.get("is_high_value"),
            "churn_score": state.get("churn_score"),
            "churn_decile": state.get("churn_decile"),
            "intention_score": state.get("intention_score"),
            "intention_decile": state.get("intention_decile"),
            "risk_pattern": state.get("risk_pattern"),
            "top_drivers": state.get("top_drivers")
        },
        "voice_of_customer_context": {
            "cluster_id": state.get("cluster_id"),
            "motive_dist": state.get("voice_context", {}).get("motive_distribution", [])[:3] if state.get("voice_context") else []
        },
        "decision": {
            "action": state.get("recommended_action"),
            "discount_pct": state.get("discount_pct"),
            "discount_months": state.get("discount_duration_months"),
            "economic_impact": state.get("economic_impact"),
            "hitl_applied": state.get("hitl_required"),
            "human_resolution": state.get("human_decision")
        },
        "audit_trace": {
            "evidence_refs": state.get("evidence_refs"),
            "policy_flags": state.get("policy_flags"),
            "judge_evaluation": state.get("judge_scores"),
            "retries": state.get("retry_count")
        }
    }
    return {"final_output": final_output}


# ------------------------------------------------------------------------------
# 2. Ruteo y Aristas Condicionales
# ------------------------------------------------------------------------------

def route_after_judge(state: OrchestratorState) -> Literal["retention_orchestrator", "policy_gate"]:
    """Bucle de reintento: Si el juez reprueba y retry_count == 1, reintenta."""
    passed = state.get("judge_passed", True)
    retry_count = state.get("retry_count", 0)

    if not passed and retry_count <= 1:
        return "retention_orchestrator"
    return "policy_gate"


def route_after_policy_gate(state: OrchestratorState) -> Literal["human_review", "finalize"]:
    """Compuerta de decisión: Si requiere HITL se desvía a revisión humana."""
    if state.get("hitl_required", False):
        return "human_review"
    return "finalize"


# ------------------------------------------------------------------------------
# 3. Construcción del Grafo Stateful
# ------------------------------------------------------------------------------

def build_retention_graph():
    """Construye y compila el StateGraph con checkpointer en memoria."""
    workflow = StateGraph(OrchestratorState)

    # Agregar Nodos
    workflow.add_node("validate_request", validate_request_node)
    workflow.add_node("customer_agent", customer_agent_node)
    workflow.add_node("voc_agent", voc_agent_node)
    workflow.add_node("merge_evidence", merge_evidence_node)
    workflow.add_node("retention_orchestrator", retention_orchestrator_node)
    workflow.add_node("deterministic_guardrails", deterministic_guardrails_node)
    workflow.add_node("judge", judge_agent_node)
    workflow.add_node("policy_gate", policy_gate_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("final_validation", final_validation_node)
    workflow.add_node("finalize", finalize_node)

    # Definir Aristas (Flujo)
    workflow.add_edge(START, "validate_request")
    
    # Ramificación paralela a ambos agentes
    workflow.add_edge("validate_request", "customer_agent")
    workflow.add_edge("validate_request", "voc_agent")
    
    # Convergencia en merge_evidence
    workflow.add_edge("customer_agent", "merge_evidence")
    workflow.add_edge("voc_agent", "merge_evidence")

    # Flujo secuencial hacia el Orquestador y Juez
    workflow.add_edge("merge_evidence", "retention_orchestrator")
    workflow.add_edge("retention_orchestrator", "deterministic_guardrails")
    workflow.add_edge("deterministic_guardrails", "judge")

    # Ruteo condicional desde el Juez (Retry Loop)
    workflow.add_conditional_edges(
        "judge",
        route_after_judge,
        {
            "retention_orchestrator": "retention_orchestrator",
            "policy_gate": "policy_gate"
        }
    )

    # Ruteo condicional de HITL
    workflow.add_conditional_edges(
        "policy_gate",
        route_after_policy_gate,
        {
            "human_review": "human_review",
            "finalize": "finalize"
        }
    )

    workflow.add_edge("human_review", "final_validation")
    workflow.add_edge("final_validation", "finalize")
    workflow.add_edge("finalize", END)

    # Checkpointer para persistencia y soporte de interrupt()
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    return app
