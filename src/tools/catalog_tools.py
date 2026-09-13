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


# ------------------------------------------------------------------------------
# Parámetros Empíricos y Escenarios de Retención (Gate 4)
# ------------------------------------------------------------------------------
# Tasas empíricas reales observadas en el Development Set (16.000 clientes)
# Evita la distorsión del score probabilístico causada por scale_pos_weight
EMPIRICAL_CHURN_RATES: Dict[int, float] = {
    1: 0.0519,  # 5.19% real observado en Decil 1 (concentra el 90-100% de churners)
    2: 0.0025,  # 0.25% observado
    3: 0.0005,  # residual
    4: 0.0005,
    5: 0.0005,
    6: 0.0002,
    7: 0.0002,
    8: 0.0001,
    9: 0.00005,
    10: 0.00001
}

# Escenarios de Uplift Incremental de Retención solicitados por el Comité
UPLIFT_SCENARIOS: Dict[str, float] = {
    "conservative": 0.10,  # 10% de efectividad de retención incremental
    "base": 0.20,          # 20% de efectividad (Escenario base telecomunicaciones)
    "optimistic": 0.30     # 30% de efectividad (Escenario óptimo intervención oportuna)
}


def get_catalog() -> Dict[str, Any]:
    """Retorna el catálogo completo de acciones de retención disponibles."""
    return {k: v.model_dump() for k, v in ACTION_CATALOG.items()}


def estimate_economic_impact(
    arpu_cop: float,
    churn_prob: Optional[float] = None,
    churn_decile: Optional[int] = 1,
    action_id: str = "PRIORITY_TECH_VISIT",
    discount_pct: float = 0.0,
    discount_months: int = 1,
    uplift_scenario: str = "base"
) -> Dict[str, Any]:
    """
    Calcula la ecuación financiera de impacto de retención para un cliente individual:
    - Utiliza la tasa empírica observada por decil para evitar el sesgo de calibración
      por ponderación de clases (scale_pos_weight).
    - Aplica escenarios de uplift incremental: Conservador (10%), Base (20%), Optimista (30%).

    Ecuación Financiera:
      Tasa Riesgo Real = Tasa Empírica del Decil (ej. 5.19% para Decil 1)
      Valor Anual Salvado = ARPU * 12 meses * Tasa Riesgo Real * Factor Uplift
      Costo Intervención = Costo Operativo Directo + (ARPU * Descuento % * Meses de Descuento)
      Beneficio Neto = Valor Anual Salvado - Costo Intervención
      ROI Multiplicador = Beneficio Neto / Costo Intervención
    """
    if action_id not in ACTION_CATALOG:
        return {"error": "Acción fuera de catálogo", "net_roi": 0.0}

    action = ACTION_CATALOG[action_id]

    # Determinar tasa de riesgo real: preferir tasa empírica por decil
    if churn_decile is not None and churn_decile in EMPIRICAL_CHURN_RATES:
        effective_churn_rate = EMPIRICAL_CHURN_RATES[churn_decile]
        rate_source = f"Empirical Decile {churn_decile}"
    elif churn_prob is not None:
        effective_churn_rate = float(churn_prob)
        rate_source = "Raw Model Probability"
    else:
        effective_churn_rate = EMPIRICAL_CHURN_RATES[1]
        rate_source = "Default Decile 1 Empirical"

    # Factor de efectividad según escenario
    uplift = UPLIFT_SCENARIOS.get(uplift_scenario.lower(), 0.20)

    # Cálculo financiero anualizado
    annual_revenue = arpu_cop * 12.0
    expected_churn_loss_prevented = annual_revenue * effective_churn_rate * uplift

    cost_direct = action.cost_cop
    cost_discount = arpu_cop * discount_pct * discount_months
    total_cost = cost_direct + cost_discount

    net_value = expected_churn_loss_prevented - total_cost
    roi = (net_value / total_cost) if total_cost > 0 else 0.0

    # Sensibilidad a los 3 escenarios
    scenarios_impact = {}
    for sc_name, sc_uplift in UPLIFT_SCENARIOS.items():
        sc_loss_prevented = annual_revenue * effective_churn_rate * sc_uplift
        sc_net = sc_loss_prevented - total_cost
        sc_roi = (sc_net / total_cost) if total_cost > 0 else 0.0
        scenarios_impact[sc_name] = {
            "uplift_pct": round(sc_uplift * 100, 1),
            "expected_prevented_cop": round(sc_loss_prevented, 2),
            "net_value_cop": round(sc_net, 2),
            "roi_multiplier": round(sc_roi, 2)
        }

    return {
        "arpu_cop": round(arpu_cop, 2),
        "annual_arpu_value": round(annual_revenue, 2),
        "rate_source": rate_source,
        "effective_churn_rate": round(effective_churn_rate, 4),
        "uplift_scenario_applied": uplift_scenario,
        "uplift_applied_pct": round(uplift * 100, 1),
        "expected_prevented_loss": round(expected_churn_loss_prevented, 2),
        "intervention_cost_total": round(total_cost, 2),
        "net_economic_value": round(net_value, 2),
        "estimated_roi_multiplier": round(roi, 2),
        "scenarios_breakdown": scenarios_impact
    }


def project_cluster_portfolio_impact(
    total_population: int = 20000,
    target_decile_pct: float = 0.10,
    mean_arpu_cop: float = 96446.78,
    empirical_churn_rate_decile1: float = 0.0519,
    avg_intervention_cost_cop: float = 28000.0
) -> Dict[str, Any]:
    """
    Proyecta el impacto económico agregado a nivel de todo el Cluster 3 (20.000 clientes)
    al intervenir de forma focalizada el Top 10% (Decil 1 = 2.000 clientes).
    """
    target_clients = int(total_population * target_decile_pct)
    annual_arpu_per_client = mean_arpu_cop * 12.0
    total_annual_revenue_target = target_clients * annual_arpu_per_client

    # Total de clientes que desertarían sin intervención en Decil 1
    expected_churners_natural = target_clients * empirical_churn_rate_decile1
    total_annual_loss_natural = expected_churners_natural * annual_arpu_per_client

    total_campaign_cost = target_clients * avg_intervention_cost_cop

    scenarios = {}
    for sc_name, uplift in UPLIFT_SCENARIOS.items():
        retained_clients = expected_churners_natural * uplift
        revenue_saved = retained_clients * annual_arpu_per_client
        net_profit = revenue_saved - total_campaign_cost
        roi = (net_profit / total_campaign_cost) if total_campaign_cost > 0 else 0.0

        scenarios[sc_name] = {
            "uplift_label": f"{int(uplift * 100)}%",
            "retained_clients": round(retained_clients, 1),
            "gross_revenue_saved_cop": round(revenue_saved, 2),
            "campaign_cost_cop": round(total_campaign_cost, 2),
            "net_economic_benefit_cop": round(net_profit, 2),
            "roi_ratio": round(roi, 2)
        }

    return {
        "cluster_total_clients": total_population,
        "target_clients_decil_1": target_clients,
        "mean_arpu_cop": round(mean_arpu_cop, 2),
        "target_pool_annual_revenue_cop": round(total_annual_revenue_target, 2),
        "expected_churners_decil_1": round(expected_churners_natural, 1),
        "expected_annual_loss_without_action_cop": round(total_annual_loss_natural, 2),
        "total_campaign_cost_cop": round(total_campaign_cost, 2),
        "scenarios": scenarios
    }

