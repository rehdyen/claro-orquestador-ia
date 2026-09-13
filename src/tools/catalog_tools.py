"""
src/tools/catalog_tools.py
==========================
Catálogo oficial de acciones comerciales y técnicas para retención de clientes.
Define costos, reglas de elegibilidad, límites de descuento y cálculo de ROI económico.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class RetentionAction(BaseModel):
    action_id: str
    action_name: str
    action_type: str  # "TECHNICAL", "COMMERCIAL", "CONTRACTUAL", "DIAGNOSTIC", "ABSTAIN"
    cost_cop: float
    max_discount_pct: float = 0.0
    max_duration_months: int = 0
    requires_hitl: bool = False
    senior_review_required: bool = False
    description: str
    eligibility_criteria: str


# ------------------------------------------------------------------------------
# Catálogo Maestro de Acciones de Retención (Claro Colombia — Cluster 3)
# ------------------------------------------------------------------------------
ACTION_CATALOG: Dict[str, RetentionAction] = {
    "PRIORITY_TECH_VISIT": RetentionAction(
        action_id="PRIORITY_TECH_VISIT",
        action_name="Visita Técnica Prioritaria & Certificación de Red",
        action_type="TECHNICAL",
        cost_cop=35000.0,
        requires_hitl=False,  # Auto-recomendable si hay falla técnica
        description="Envío de cuadrilla técnica especializada en menos de 24 horas para revisión de acometida, módem y decodificadores.",
        eligibility_criteria="VAL_RECLAMOS_MES >= 1 o VELOCIDAD_INTERNET_MBPS < 50 o reporte de falla técnica."
    ),
    "SPEED_UPGRADE": RetentionAction(
        action_id="SPEED_UPGRADE",
        action_name="Upgrade de Velocidad de Internet (Fidelización Técnica)",
        action_type="CONTRACTUAL",
        cost_cop=15000.0,
        requires_hitl=True,  # Modifica producto
        description="Aumento temporal o definitivo del ancho de banda (ej. de 100 a 200 Mbps) sin costo adicional por 6 meses.",
        eligibility_criteria="Doble play / Triple play con red de fibra (FTTH) y quejas por lentitud."
    ),
    "TEMP_RENT_DISCOUNT": RetentionAction(
        action_id="TEMP_RENT_DISCOUNT",
        action_name="Descuento Temporal en Renta Mensual (Alivio Tarifario)",
        action_type="COMMERCIAL",
        cost_cop=0.0,  # El costo es el descuento otorgado sobre el ARPU
        max_discount_pct=0.20,  # 20% umbral de gobierno
        max_duration_months=3,
        requires_hitl=True,  # Afecta precio -> siempre HITL
        description="Descuento del 10% al 20% en la factura por un periodo de 2 a 3 meses condicionado a permanencia.",
        eligibility_criteria="VAL_VAR_RENTA > 0 o sensibilidad alta a precio y antigüedad > 12 meses."
    ),
    "LOYALTY_BONUS": RetentionAction(
        action_id="LOYALTY_BONUS",
        action_name="Bono de Fidelización / Paquete Premium Bonificado",
        action_type="COMMERCIAL",
        cost_cop=22000.0,
        max_duration_months=3,
        requires_hitl=True,
        description="Activación bonificada por 3 meses de paquete premium (ej. Win Sports+, HBO Max o Disney+) sin costo.",
        eligibility_criteria="Cliente caza-ofertas o con amenaza directa de migración a la competencia."
    ),
    "PREVENTIVE_DIAGNOSTIC": RetentionAction(
        action_id="PREVENTIVE_DIAGNOSTIC",
        action_name="Diagnóstico Preventivo & Llamada de Fidelización VIP",
        action_type="DIAGNOSTIC",
        cost_cop=8000.0,
        requires_hitl=True,  # Para Silent Churn
        description="Contacto proactivo por parte de un gestor senior de experiencia para auditar satisfacción antes de que el cliente deserte.",
        eligibility_criteria="Patrón de Silent Churn (Riesgo de Churn Decil 1 con baja intención registrada)."
    ),
    "ABSTAIN_NO_ACTION": RetentionAction(
        action_id="ABSTAIN_NO_ACTION",
        action_name="Sin Acción / Abstención por Riesgo Bajo o Evidencia Insuficiente",
        action_type="ABSTAIN",
        cost_cop=0.0,
        requires_hitl=False,
        description="No se interviene al cliente para evitar canibalización de ingresos o por falta de datos concluyentes.",
        eligibility_criteria="Clientes en deciles saludables (Decil 7 a 10) o con banderas de evidencia insuficiente."
    )
}


def get_catalog() -> Dict[str, Any]:
    """Retorna el catálogo completo de acciones de retención disponibles."""
    return {k: v.model_dump() for k, v in ACTION_CATALOG.items()}


def estimate_economic_impact(
    arpu_cop: float,
    churn_prob: float,
    action_id: str,
    discount_pct: float = 0.0,
    discount_months: int = 1
) -> Dict[str, float]:
    """
    Calcula la ecuación financiera de impacto de retención:
    Valor Anual Salvado = ARPU * 12 meses * Factor de Efectividad
    Costo de Intervención = Costo Fijo de Acción + (ARPU * Descuento % * Meses de Descuento)
    ROI Neto = (Valor Anual Salvado - Costo Intervención) / Costo Intervención
    """
    if action_id not in ACTION_CATALOG:
        return {"error": "Acción fuera de catálogo", "net_roi": 0.0}

    action = ACTION_CATALOG[action_id]
    
    # Asumimos una efectividad de retención estimada del 60% sobre el riesgo
    effectiveness = 0.60
    expected_churn_cost_prevented = arpu_cop * 12 * churn_prob * effectiveness

    cost_direct = action.cost_cop
    cost_discount = arpu_cop * discount_pct * discount_months
    total_cost = cost_direct + cost_discount

    net_value = expected_churn_cost_prevented - total_cost
    roi = (net_value / total_cost) if total_cost > 0 else 0.0

    return {
        "arpu_cop": round(arpu_cop, 2),
        "annual_arpu_value": round(arpu_cop * 12, 2),
        "expected_prevented_loss": round(expected_churn_cost_prevented, 2),
        "intervention_cost_total": round(total_cost, 2),
        "net_economic_value": round(net_value, 2),
        "estimated_roi_multiplier": round(roi, 2)
    }
