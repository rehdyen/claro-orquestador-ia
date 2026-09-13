"""
src/agents/voc_agent.py
=======================
NLP / Voice of Customer Agent:
Consulta el activo analítico generado en Gate 1 (outputs/nlp/resumen_voz_cliente.json)
y entrega el contexto colectivo de fricción del Cluster 3 sin forzar uniones 1:1.
"""

from typing import Dict, Any
from src.agents.state import OrchestratorState
from src.tools.nlp_tools import get_voice_profile


def voc_agent_node(state: OrchestratorState) -> Dict[str, Any]:
    """Nodo para proveer el contexto agregado de Voz del Cliente."""
    cluster_id = state.get("cluster_id", 3)

    try:
        profile = get_voice_profile(cluster_id=cluster_id)
        voc_data = profile.model_dump()
        
        evidence_tags = [
            f"Voz Cliente Cluster {cluster_id}: {voc_data['calls_analyzed']} llamadas analizadas.",
            f"Motivo Líder Cluster {cluster_id}: {voc_data['motive_distribution'][0]['motive']} ({voc_data['motive_distribution'][0]['pct']}%)" if voc_data['motive_distribution'] else "Sin motivos",
            f"Sentimiento Negativo/Mixto en Cluster: {round((voc_data['sentiment_distribution'].get('NEGATIVE', 0) + voc_data['sentiment_distribution'].get('MIXED', 0)) / max(1, voc_data['calls_analyzed']) * 100, 1)}%"
        ]
        
        return {
            "voice_context": voc_data,
            "evidence_refs": evidence_tags
        }
    except Exception as e:
        return {
            "voice_context": {"error": f"No se pudo cargar el perfil de voz: {str(e)}"},
            "policy_flags": ["VOC_PROFILE_UNAVAILABLE"]
        }
