"""
src/tools/nlp_tools.py
======================
Herramientas analíticas y contratos Pydantic para el Agente de Voz del Cliente (NLP).
Implementa la taxonomía congelada taxonomy_v1 y utilidades de consulta de perfiles de voz.
"""

from typing import Literal, List, Dict, Any, Optional
import json
import os
from pathlib import Path
from pydantic import BaseModel, Field, field_validator


# ------------------------------------------------------------------------------
# 1. Contratos Pydantic de Entrada y Salida (Data Contracts)
# ------------------------------------------------------------------------------

class EvidenceSpan(BaseModel):
    """Cita textual explícita que justifica la clasificación."""
    speaker: Literal["CLIENT", "AGENT", "UNKNOWN"] = Field(
        ..., description="Hablante que emite la frase."
    )
    text: str = Field(
        ..., min_length=3, description="Fragmento literal de la transcripción."
    )


class CallInput(BaseModel):
    """Entrada bruta para el análisis de una llamada."""
    call_id: str = Field(..., description="Identificador único de la llamada.")
    cluster: int = Field(..., description="Cluster al que pertenece la llamada.")
    transcription: str = Field(..., min_length=5, description="Texto transcrito de la llamada.")


class CallInsight(BaseModel):
    """Salida estructurada y verificable de la clasificación de una llamada."""
    call_id: str
    cluster: int

    primary_motive: str = Field(
        ..., description="Motivo principal según taxonomy_v1 o UNRESOLVED."
    )
    submotive: str = Field(
        ..., description="Submotivo específico dentro del motivo principal."
    )

    sentiment: Literal["POSITIVE", "NEUTRAL", "NEGATIVE", "MIXED"] = Field(
        ..., description="Sentimiento manifestado por el CLIENTE (no por el asesor)."
    )

    urgency: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        ..., description="Nivel de urgencia deducido estrictamente de la conversación."
    )

    evidence: List[EvidenceSpan] = Field(
        default_factory=list,
        description="Lista de citas textuales de soporte. Obligatorio si status == 'OK'."
    )

    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Nivel de certeza operacional de la clasificación."
    )

    taxonomy_version: str = "taxonomy_v1"
    prompt_version: str = "nlp_agent_v1"
    schema_version: str = "1.0.0"

    status: Literal["OK", "UNRESOLVED", "INSUFFICIENT_EVIDENCE"] = "OK"

    @field_validator("status")
    @classmethod
    def validate_evidence_if_ok(cls, v: str, info) -> str:
        """Regla de Oro: Todo status OK debe contener al menos un evidence_span."""
        evidence = info.data.get("evidence", [])
        motive = info.data.get("primary_motive", "")
        if v == "OK" and motive != "UNRESOLVED" and len(evidence) == 0:
            raise ValueError("Las clasificaciones OK deben incluir al menos un EvidenceSpan de soporte.")
        return v


# ------------------------------------------------------------------------------
# 2. Contratos para Tools de Taxonomía y Consulta
# ------------------------------------------------------------------------------

class TaxonomyItem(BaseModel):
    motive: str
    definition: str
    allowed_submotives: List[str]


class GetTaxonomyOutput(BaseModel):
    version: str
    name: str
    status: str
    items: List[TaxonomyItem]


class GetCallInsightOutput(BaseModel):
    call_id: str
    found: bool
    insight: Optional[CallInsight] = None
    error_message: Optional[str] = None


class VoiceProfileOutput(BaseModel):
    cluster_id: int
    calls_analyzed: int
    motive_distribution: List[Dict[str, Any]]
    submotive_distribution: List[Dict[str, Any]]
    sentiment_distribution: Dict[str, int]
    urgency_distribution: Dict[str, int]
    top_friction_evidence: List[str]
    taxonomy_version: str = "taxonomy_v1"


# ------------------------------------------------------------------------------
# 3. Implementación de Tools
# ------------------------------------------------------------------------------

def get_taxonomy(version: str = "taxonomy_v1") -> GetTaxonomyOutput:
    """Carga y retorna la taxonomía congelada oficial para el análisis de llamadas."""
    tax_path = Path("data/processed/taxonomy_v1.json")
    if not tax_path.exists():
        # Fallback si se ejecuta desde subcarpetas
        tax_path = Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "taxonomy_v1.json"

    with open(tax_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return GetTaxonomyOutput(**data)


def get_call_insight(call_id: str, results_path: Optional[str] = None) -> GetCallInsightOutput:
    """Consulta una llamada previamente procesada en el almacén de resultados NLP."""
    if results_path is None:
        results_path = "outputs/nlp/llamadas_procesadas.json"

    p = Path(results_path)
    if not p.exists():
        return GetCallInsightOutput(
            call_id=call_id,
            found=False,
            error_message=f"Archivo de resultados {results_path} no encontrado."
        )

    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Buscar llamada por ID
    for item in data.get("llamadas", []):
        if str(item.get("call_id")) == str(call_id):
            return GetCallInsightOutput(
                call_id=call_id,
                found=True,
                insight=CallInsight(**item)
            )

    return GetCallInsightOutput(
        call_id=call_id,
        found=False,
        error_message=f"Llamada {call_id} no encontrada en los resultados."
    )


def get_voice_profile(cluster_id: int, results_path: Optional[str] = None) -> VoiceProfileOutput:
    """
    Agrega estadísticamente los insights NLP para un cluster específico.
    Permite contrastar la voz del cliente del Cluster 3 frente al resto de la base.
    """
    if results_path is None:
        results_path = "outputs/nlp/llamadas_procesadas.json"

    p = Path(results_path)
    if not p.exists():
        raise FileNotFoundError(f"Resultados no encontrados en {results_path}")

    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    cluster_calls = [
        CallInsight(**item)
        for item in data.get("llamadas", [])
        if item.get("cluster") == cluster_id
    ]

    total = len(cluster_calls)
    if total == 0:
        return VoiceProfileOutput(
            cluster_id=cluster_id,
            calls_analyzed=0,
            motive_distribution=[],
            submotive_distribution=[],
            sentiment_distribution={},
            urgency_distribution={},
            top_friction_evidence=[]
        )

    # Conteo de motivos
    motive_counts: Dict[str, int] = {}
    submotive_counts: Dict[str, int] = {}
    sentiment_counts: Dict[str, int] = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0, "MIXED": 0}
    urgency_counts: Dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    evidence_samples: List[str] = []

    for c in cluster_calls:
        motive_counts[c.primary_motive] = motive_counts.get(c.primary_motive, 0) + 1
        submotive_counts[c.submotive] = submotive_counts.get(c.submotive, 0) + 1
        sentiment_counts[c.sentiment] = sentiment_counts.get(c.sentiment, 0) + 1
        urgency_counts[c.urgency] = urgency_counts.get(c.urgency, 0) + 1

        if c.urgency in ["HIGH", "CRITICAL"] and len(evidence_samples) < 5:
            for ev in c.evidence:
                if ev.speaker == "CLIENT":
                    evidence_samples.append(f"[Call {c.call_id}] {ev.text}")
                    break

    motive_dist = [
        {"motive": m, "count": count, "pct": round(count / total * 100, 2)}
        for m, count in sorted(motive_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    submotive_dist = [
        {"submotive": sm, "count": count, "pct": round(count / total * 100, 2)}
        for sm, count in sorted(submotive_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    return VoiceProfileOutput(
        cluster_id=cluster_id,
        calls_analyzed=total,
        motive_distribution=motive_dist,
        submotive_distribution=submotive_dist,
        sentiment_distribution=sentiment_counts,
        urgency_distribution=urgency_counts,
        top_friction_evidence=evidence_samples
    )
