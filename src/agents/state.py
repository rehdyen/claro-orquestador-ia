"""
src/agents/state.py
===================
Definición del estado global y contratos compartidos en LangGraph (StateGraph).
Mantiene explícitamente toda la evidencia analítica, scores, drivers, decisiones y trazas HITL.
Usa Annotated con operator.add para soportar actualizaciones concurrentes en ramas paralelas.
"""

from operator import add
from typing import Annotated, TypedDict, Optional, List, Dict, Any, Literal


class OrchestratorState(TypedDict):
    # Identificadores de sesión y auditoría
    run_id: str
    thread_id: str
    request: Dict[str, Any]

    # Datos de entrada del cliente y cluster
    cluster_id: int
    record_uid: Optional[str]
    customer_record: Dict[str, Any]

    # Contexto NLP (Voz del Cliente agregada de Cluster 3)
    voice_context: Optional[Dict[str, Any]]

    # Contexto Analítico Estructurado (Customer Intelligence)
    customer_context: Optional[Dict[str, Any]]
    churn_score: Optional[float]
    churn_decile: Optional[int]
    intention_score: Optional[float]
    intention_decile: Optional[int]
    arpu: Optional[float]
    is_high_value: bool
    risk_pattern: Optional[str]  # "CRITICAL_BOTH", "SILENT_CHURN_PATTERN", "CHURN_DOMINANT", etc.
    top_drivers: List[Dict[str, Any]]

    # Selección de Acciones y Evaluación de Negocio
    candidate_actions: List[Dict[str, Any]]
    recommended_action: Optional[Dict[str, Any]]
    action_cost: float
    discount_pct: float
    discount_duration_months: int
    economic_impact: Optional[Dict[str, Any]]

    # Gobernanza, Trazabilidad y Guardrails (con reducers para ramas paralelas)
    evidence_refs: Annotated[List[str], add]
    policy_flags: Annotated[List[str], add]

    # Evaluación y Juez (Judge)
    judge_scores: Optional[Dict[str, Any]]
    judge_passed: bool
    retry_count: int

    # Human-in-the-Loop (HITL)
    hitl_required: bool
    senior_review_required: bool
    hitl_reasons: List[str]
    human_decision: Optional[Dict[str, Any]]

    # Salida Definitiva
    final_output: Optional[Dict[str, Any]]
