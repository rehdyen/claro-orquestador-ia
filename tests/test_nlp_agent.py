"""
tests/test_nlp_agent.py
=======================
Pruebas unitarias automatizadas para el Agente NLP y herramientas de Voz del Cliente.
Verifica cumplimiento estricto de esquemas Pydantic, taxonomía cerrada y guardrails.
"""

import pytest
from src.tools.nlp_tools import (
    CallInput,
    CallInsight,
    EvidenceSpan,
    get_taxonomy,
    GetTaxonomyOutput
)
from src.agents.nlp_agent import NLPAgent, DomainSemanticExtractor


@pytest.fixture
def agent():
    return NLPAgent()


def test_taxonomy_loading(agent):
    """Verifica que la taxonomía v1 congelada cargue correctamente con todos sus motivos."""
    tax = agent.taxonomy
    assert isinstance(tax, GetTaxonomyOutput)
    assert tax.version == "taxonomy_v1"
    assert tax.status == "FROZEN"
    motives = [item.motive for item in tax.items]
    assert "FALLA_TECNICA" in motives
    assert "FACTURACION_Y_COBROS" in motives
    assert "PRECIO_Y_COMPETENCIA" in motives
    assert "ATENCION_Y_CUMPLIMIENTO" in motives
    assert "MUDANZA_Y_TRASLADO" in motives
    assert "UNRESOLVED" in motives


def test_classify_falla_tecnica(agent):
    """Verifica clasificación precisa de reclamo por falla de internet."""
    transcript = (
        "AGENT: Buenas tardes, habla con Claro. ¿En qué le puedo servir?\n"
        "CLIENT: Buenas tardes, es que el internet está muy lento, se cae a cada rato y no me sirve para trabajar.\n"
        "AGENT: Entiendo su problema, vamos a revisar el módem."
    )
    call = CallInput(call_id="test_01", cluster=3, transcription=transcript)
    insight = agent.analyze_call(call)

    assert isinstance(insight, CallInsight)
    assert insight.primary_motive == "FALLA_TECNICA"
    assert insight.submotive == "INTERNET_LENTO_INTERMITENTE"
    assert insight.status == "OK"
    assert len(insight.evidence) >= 1
    assert insight.confidence >= 0.7


def test_classify_facturacion_paquete_no_solicitado(agent):
    """Verifica clasificación precisa de cobro de paquete no solicitado (ej. Llamada 2 real)."""
    transcript = (
        "AGENT: Área de cancelaciones, con quién hablo.\n"
        "CLIENT: Estoy furioso, me llegó la factura con un paquete internacional que no pedí y me lo siguen cobrando.\n"
        "AGENT: Permítame validar su número de cuenta."
    )
    call = CallInput(call_id="test_02", cluster=3, transcription=transcript)
    insight = agent.analyze_call(call)

    assert insight.primary_motive == "FACTURACION_Y_COBROS"
    assert insight.submotive == "COBRO_SERVICIO_NO_SOLICITADO"
    assert insight.sentiment == "NEGATIVE"
    assert insight.status == "OK"
    assert len(insight.evidence) >= 1


def test_classify_unresolved_on_short_text(agent):
    """Verifica abstención y UNRESOLVED cuando el audio es inaudible o muy corto (Guardrail G-NLP-06)."""
    call = CallInput(call_id="test_03", cluster=3, transcription="Aló... aló? sí?")
    insight = agent.analyze_call(call)

    assert insight.primary_motive == "UNRESOLVED"
    assert insight.submotive == "AUDIO_INAUDIBLE_CORTO"
    assert insight.status == "UNRESOLVED"


def test_pydantic_schema_integrity():
    """Garantiza que no se puedan crear CallInsight inválidos sin evidencia si status == OK."""
    with pytest.raises(ValueError):
        CallInsight(
            call_id="test_invalid",
            cluster=3,
            primary_motive="FALLA_TECNICA",
            submotive="INTERNET_LENTO_INTERMITENTE",
            sentiment="NEGATIVE",
            urgency="HIGH",
            evidence=[],  # Vacío deliberadamente
            confidence=0.8,
            status="OK"
        )
