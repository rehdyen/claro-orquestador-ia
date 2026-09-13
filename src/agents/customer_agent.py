"""
src/agents/customer_agent.py
============================
Customer Intelligence Agent:
Consulta los modelos predictivos duales (LightGBM) y herramientas analíticas.
Extrae scores, deciles poblacionales, patrón de riesgo y top drivers SHAP.
"""

from typing import Dict, Any
from src.agents.state import OrchestratorState
from src.tools.customer_tools import CustomerIntelligenceTools

tools = CustomerIntelligenceTools()


def customer_agent_node(state: OrchestratorState) -> Dict[str, Any]:
    """Nodo analítico para procesar la información estructurada del cliente."""
    record = state.get("customer_record", {})
    if not record:
        return {
            "customer_context": {"error": "Registro de cliente no provisto."},
            "policy_flags": ["MISSING_CUSTOMER_RECORD"]
        }

    # Scoring y deciles
    res = tools.score_customer(record)

    evidence_tags = [
        f"Churn Score: {res['churn_score']} (Decil {res['churn_decile']})",
        f"Intención Score: {res['intention_score']} (Decil {res['intention_decile']})",
        f"ARPU: ${res['arpu']:,.0f} COP ({'Alto Valor >= P75' if res['is_high_value'] else 'Estándar'})",
        f"Patrón de Riesgo: {res['risk_pattern']}"
    ]

    for d in res["top_drivers"]:
        evidence_tags.append(f"Top Driver: {d['feature']} (SHAP: {d['shap_value']})")

    return {
        "customer_context": res,
        "churn_score": res["churn_score"],
        "churn_decile": res["churn_decile"],
        "intention_score": res["intention_score"],
        "intention_decile": res["intention_decile"],
        "arpu": res["arpu"],
        "is_high_value": res["is_high_value"],
        "risk_pattern": res["risk_pattern"],
        "top_drivers": res["top_drivers"],
        "evidence_refs": evidence_tags
    }
