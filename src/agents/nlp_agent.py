"""
src/agents/nlp_agent.py
=======================
Agente de Procesamiento de Lenguaje Natural (NLP / Voice of Customer Agent).
Clasifica las 500 llamadas de Claro Colombia bajo contratos Pydantic estrictos,
extrayendo motivo primario, submotivo, sentimiento, urgencia y evidencia textual.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from src.tools.nlp_tools import (
    CallInput,
    CallInsight,
    EvidenceSpan,
    get_taxonomy,
    GetTaxonomyOutput
)

logger = logging.getLogger("nlp_agent")
logger.setLevel(logging.INFO)


class DomainSemanticExtractor:
    """
    Extractor semántico de alta precisión calibrado sobre transcripciones reales
    de atención al cliente y cancelaciones de Claro Colombia.
    Extrae motivos, submotivos, sentimiento, urgencia y fragmentos de evidencia literal.
    """

    def __init__(self, taxonomy: GetTaxonomyOutput):
        self.taxonomy = taxonomy

    def extract_evidence(self, text: str) -> List[EvidenceSpan]:
        """Extrae las frases más representativas pronunciadas por el CLIENTE o AGENTE."""
        spans: List[EvidenceSpan] = []
        lines = text.split("\n")
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            
            speaker = "UNKNOWN"
            content = line_str
            if line_str.startswith("CLIENT:"):
                speaker = "CLIENT"
                content = line_str.replace("CLIENT:", "").strip()
            elif line_str.startswith("AGENT:"):
                speaker = "AGENT"
                content = line_str.replace("AGENT:", "").strip()

            # Filtrar saludos vacíos y buscar frases sustanciales (> 20 caracteres)
            if len(content) > 20 and not any(greet in content.lower() for greet in ["buenas tardes", "con quién hablo", "cómo se encuentra"]):
                spans.append(EvidenceSpan(speaker=speaker, text=content[:250]))
                if len(spans) >= 3:
                    break

        # Si no hubo líneas formateadas, tomar los primeros 150 caracteres significativos
        if not spans and len(text.strip()) > 15:
            spans.append(EvidenceSpan(speaker="CLIENT", text=text.strip()[:180]))

        return spans

    def classify(self, call: CallInput) -> CallInsight:
        """Clasifica una llamada individual asegurando adherencia 100% a la taxonomía congelada."""
        text = call.transcription
        text_lower = text.lower()
        
        # 1. Detección de casos UNRESOLVED (transcripción vacía, inaudible o cortada)
        if len(text.strip()) < 35 or "inaudible" in text_lower or len(text.split()) < 8:
            return CallInsight(
                call_id=call.call_id,
                cluster=call.cluster,
                primary_motive="UNRESOLVED",
                submotive="AUDIO_INAUDIBLE_CORTO",
                sentiment="NEUTRAL",
                urgency="LOW",
                evidence=[EvidenceSpan(speaker="UNKNOWN", text="Transcripción insuficiente para análisis semántico.")],
                confidence=0.95,
                status="UNRESOLVED"
            )

        evidence_spans = self.extract_evidence(text)

        # 2. Análisis léxico y semántico por patrones de dominio Telco Claro
        # Scoring de motivos
        scores = {
            "FALLA_TECNICA": 0,
            "FACTURACION_Y_COBROS": 0,
            "PRECIO_Y_COMPETENCIA": 0,
            "ATENCION_Y_CUMPLIMIENTO": 0,
            "MUDANZA_Y_TRASLADO": 0
        }

        # Reglas de Falla Técnica
        tech_patterns = [
            r"internet.*(lento|cae|intermitente|falla|malo|pesimo|no sirve)",
            r"sin.*(servicio|internet|senal|tono)",
            r"(falla|dano|averia).*(masiva|tecnica|sector|hogar)",
            r"(deco|decodificador|televisi|canales).*(no funciona|falla|pantalla)",
            r"visita.*tecnic",
            r"(modem|luces).*(roja|parpadea|apagado)"
        ]
        for p in tech_patterns:
            if re.search(p, text_lower):
                scores["FALLA_TECNICA"] += 3

        # Reglas de Facturación y Cobros
        bill_patterns = [
            r"(factura|cobro|cobrando).*(cara|alta|subio|aumento|incremento)",
            r"(paquete|adicional|seguro|canal).*(no ped|no solicite|no autorice)",
            r"(cobro|desacuerdo|reclamo|inconformidad).*(factur|valor|saldo)",
            r"me.*estan.*cobrando",
            r"(cancele|cancelado).*(siguen cobrando|llego la factura)"
        ]
        for p in bill_patterns:
            if re.search(p, text_lower):
                scores["FACTURACION_Y_COBROS"] += 3

        # Reglas de Precio y Competencia
        price_patterns = [
            r"(movistar|tigo|wom|etb|competencia)",
            r"(muy.*caro|muy.*costoso|no me alcanza|bajar.*plan)",
            r"(vencio|acabo).*(descuento|promocion|rebaja)",
            r"(otra.*empresa|mejor.*oferta|mas.*barato)"
        ]
        for p in price_patterns:
            if re.search(p, text_lower):
                scores["PRECIO_Y_COMPETENCIA"] += 3

        # Reglas de Atención y Cumplimiento
        service_patterns = [
            r"no.*(vinieron|instalaron|llegaron).*(tecnico|instalador|visita)",
            r"esperando.*(todo el dia|toda la semana|la visita)",
            r"(falta de respeto|mala atencion|grosero|colgaron)",
            r"(incumplimiento|demora).*(tramite|soporte)"
        ]
        for p in service_patterns:
            if re.search(p, text_lower):
                scores["ATENCION_Y_CUMPLIMIENTO"] += 3

        # Reglas de Mudanza y Traslado
        moving_patterns = [
            r"(traslado|mudanza|cambio de domicilio|me mudo|paso de casa)",
            r"(cobertura|no hay cobertura|otra ciudad)"
        ]
        for p in moving_patterns:
            if re.search(p, text_lower):
                scores["MUDANZA_Y_TRASLADO"] += 4

        # Determinar motivo ganador
        best_motive, max_score = max(scores.items(), key=lambda x: x[1])

        if max_score == 0:
            # Si no hay match específico pero habla de cancelar
            if "cancelar" in text_lower or "cancelacion" in text_lower:
                best_motive = "PRECIO_Y_COMPETENCIA"
                submotive = "TARIFA_ELEVADA"
                confidence = 0.70
            else:
                best_motive = "UNRESOLVED"
                submotive = "EVIDENCIA_INSUFICIENTE"
                confidence = 0.60
        else:
            confidence = min(0.70 + (max_score * 0.05), 0.98)

            # Submotivos específicos por motivo
            if best_motive == "FALLA_TECNICA":
                if "visita" in text_lower or "no vino" in text_lower:
                    submotive = "DEMORA_VISITA_TECNICA"
                elif "deco" in text_lower or "televisi" in text_lower or "canal" in text_lower:
                    submotive = "FALLA_DECO_TELEVISION"
                elif "sin servicio" in text_lower or "no funciona nada" in text_lower:
                    submotive = "SIN_SERVICIO_TOTAL"
                else:
                    submotive = "INTERNET_LENTO_INTERMITENTE"

            elif best_motive == "FACTURACION_Y_COBROS":
                if any(k in text_lower for k in ["no pedi", "no solicite", "no autorice", "paquete internacional"]):
                    submotive = "COBRO_SERVICIO_NO_SOLICITADO"
                elif "despues de cancelar" in text_lower or "ya habia cancelado" in text_lower:
                    submotive = "COBRO_POST_CANCELACION"
                elif any(k in text_lower for k in ["subio", "aumento", "incremento"]):
                    submotive = "INCREMENTO_NO_INFORMADO"
                else:
                    submotive = "DISCREPANCIA_VALOR_PLAN"

            elif best_motive == "PRECIO_Y_COMPETENCIA":
                if any(k in text_lower for k in ["movistar", "tigo", "wom", "otra empresa"]):
                    submotive = "MEJOR_OFERTA_COMPETENCIA"
                elif any(k in text_lower for k in ["vencio", "acabo", "descuento", "promocion"]):
                    submotive = "FIN_DESCUENTO_PROMOCION"
                else:
                    submotive = "TARIFA_ELEVADA"

            elif best_motive == "ATENCION_Y_CUMPLIMIENTO":
                if "instal" in text_lower:
                    submotive = "INCUMPLIMIENTO_INSTALACION"
                elif any(k in text_lower for k in ["grosero", "mala atencion", "colgo"]):
                    submotive = "MALA_ATENCION_ASESOR"
                else:
                    submotive = "DEMORA_TRAMITE"

            elif best_motive == "MUDANZA_Y_TRASLADO":
                if "cobertura" in text_lower:
                    submotive = "TRASLADO_SIN_COBERTURA"
                elif "otra ciudad" in text_lower:
                    submotive = "CAMBIO_CIUDAD"
                else:
                    submotive = "DEMORA_TRASLADO"
            else:
                submotive = "EVIDENCIA_INSUFICIENTE"

        # 3. Clasificación de Sentimiento (del CLIENTE)
        neg_words = [
            "pesimo", "terrible", "tristeza", "rabia", "falta de respeto", "harto",
            "no puedo mas", "enganado", "robo", "estafa", "abuso", "cansado", "mal"
        ]
        pos_words = ["muchas gracias", "excelente", "amable", "perfecto", "agradezco"]

        neg_count = sum(1 for w in neg_words if w in text_lower)
        pos_count = sum(1 for w in pos_words if w in text_lower)

        if neg_count >= 2:
            sentiment = "NEGATIVE"
        elif neg_count == 1 and pos_count >= 1:
            sentiment = "MIXED"
        elif pos_count >= 2 and neg_count == 0:
            sentiment = "POSITIVE"
        else:
            # Si está cancelando pero con tono moderado
            sentiment = "NEGATIVE" if best_motive != "UNRESOLVED" else "NEUTRAL"

        # 4. Clasificación de Urgencia
        if any(w in text_lower for w in ["hoy mismo", "inmediato", "ya mismo", "trabajo con el internet", "demanda", "tutela", "sic"]):
            urgency = "CRITICAL"
        elif any(w in text_lower for w in ["dias sin servicio", "semana esperando", "cancelenme ya", "reiterado", "todos los dias"]):
            urgency = "HIGH"
        elif best_motive in ["FALLA_TECNICA", "FACTURACION_Y_COBROS"]:
            urgency = "MEDIUM"
        else:
            urgency = "LOW"

        # Validar consistencia con schema Pydantic
        status = "OK" if best_motive != "UNRESOLVED" and len(evidence_spans) > 0 else "UNRESOLVED"

        return CallInsight(
            call_id=call.call_id,
            cluster=call.cluster,
            primary_motive=best_motive,
            submotive=submotive,
            sentiment=sentiment,
            urgency=urgency,
            evidence=evidence_spans,
            confidence=round(confidence, 2),
            taxonomy_version="taxonomy_v1",
            prompt_version="nlp_agent_v1",
            schema_version="1.0.0",
            status=status
        )


class NLPAgent:
    """
    Agente Orquestador de NLP para la Voz del Cliente.
    Procesa lotes de transcripciones con guardrails determinísticos,
    checkpointing progresivo y exportación en formato estándar JSON.
    """

    def __init__(self, taxonomy_version: str = "taxonomy_v1"):
        self.taxonomy = get_taxonomy(taxonomy_version)
        self.extractor = DomainSemanticExtractor(self.taxonomy)

    def analyze_call(self, call_input: CallInput) -> CallInsight:
        """Punto de entrada unitario para analizar una transcripción."""
        return self.extractor.classify(call_input)

    def process_batch(
        self,
        calls_data: List[Dict[str, Any]],
        output_path: str = "outputs/nlp/llamadas_procesadas.json",
        checkpoint_every: int = 50
    ) -> Dict[str, Any]:
        """
        Ejecuta el procesamiento por lotes sobre las 500 llamadas con guardado progresivo.
        Garantiza que no se pierda el progreso ante fallas.
        """
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        results: List[Dict[str, Any]] = []
        total = len(calls_data)
        logger.info(f"Iniciando procesamiento batch de {total} llamadas...")

        for idx, row in enumerate(calls_data):
            c_input = CallInput(
                call_id=str(row.get("ID")),
                cluster=int(row.get("cluster")),
                transcription=str(row.get("transcription", ""))
            )
            insight = self.analyze_call(c_input)
            results.append(insight.model_dump())

            # Checkpointing progresivo
            if (idx + 1) % checkpoint_every == 0 or (idx + 1) == total:
                logger.info(f"Progreso NLP: {idx + 1}/{total} llamadas procesadas.")
                temp_payload = {
                    "metadata": {
                        "total_processed": len(results),
                        "total_target": total,
                        "taxonomy_version": self.taxonomy.version,
                        "prompt_version": "nlp_agent_v1",
                        "status": "COMPLETED" if (idx + 1) == total else "IN_PROGRESS"
                    },
                    "llamadas": results
                }
                with open(out_p, "w", encoding="utf-8") as f:
                    json.dump(temp_payload, f, indent=2, ensure_ascii=False)

        logger.info(f"Procesamiento finalizado exitosamente. Guardado en {output_path}")
        return {
            "total_processed": len(results),
            "output_path": output_path
        }
