"""
src/tools/mcp_server.py
=======================
Servidor FastMCP — Capa de Interoperabilidad Empresarial para Claro Colombia.
Expone las herramientas analíticas de Inteligencia de Clientes, Voz del Cliente (NLP),
Catálogo de Acciones y Simulación de ROI bajo el protocolo estándar Model Context Protocol (MCP).
"""

from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

from src.tools.customer_tools import CustomerIntelligenceTools
from src.tools.nlp_tools import get_voice_profile
from src.tools.catalog_tools import get_catalog, estimate_economic_impact

# Inicializar servidor MCP corporativo
mcp = FastMCP("Claro-Retention-Orchestrator-MCP")
cust_tools = CustomerIntelligenceTools()


@mcp.tool()
def get_cluster_profile() -> Dict[str, Any]:
    """Retorna el perfil estadístico consolidado del Cluster 3 de Claro Colombia."""
    return cust_tools.get_cluster_profile()


@mcp.tool()
def score_customer(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula los scores predictivos de Churn, Intención, deciles y drivers SHAP para un cliente."""
    return cust_tools.score_customer(customer_data)


@mcp.tool()
def get_voc_insights(cluster_id: int = 3) -> Dict[str, Any]:
    """Retorna la distribución de motivos, submotivos y sentimiento de las llamadas para un cluster."""
    profile = get_voice_profile(cluster_id=cluster_id)
    return profile.model_dump()


@mcp.tool()
def get_action_catalog() -> Dict[str, Any]:
    """Consulta el catálogo maestro de acciones de retención técnica y comercial."""
    return get_catalog()


@mcp.tool()
def calculate_roi(
    arpu_cop: float,
    churn_prob: float,
    action_id: str,
    discount_pct: float = 0.0,
    discount_months: int = 1
) -> Dict[str, float]:
    """Calcula el impacto económico financiero y ROI estimado de aplicar una acción a un cliente."""
    return estimate_economic_impact(
        arpu_cop=arpu_cop,
        churn_prob=churn_prob,
        action_id=action_id,
        discount_pct=discount_pct,
        discount_months=discount_months
    )


if __name__ == "__main__":
    mcp.run()
