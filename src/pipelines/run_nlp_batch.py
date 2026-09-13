"""
src/pipelines/run_nlp_batch.py
==============================
Pipeline de procesamiento masivo para las 500 llamadas de audio transcritas de Claro Colombia.
Ejecuta el Agente NLP, valida contra Pydantic y exporta outputs/nlp/llamadas_procesadas.json.
Genera estadísticas descriptivas para Cluster 3 vs Otros Clusters.
"""

import sys
import json
import logging
from pathlib import Path
import pandas as pd

# Asegurar path de importación
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.agents.nlp_agent import NLPAgent
from src.tools.nlp_tools import get_voice_profile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("nlp_pipeline")


def main():
    logger.info("Cargando dataset de llamadas desde data/processed/llamadas.parquet...")
    df_l = pd.read_parquet("data/processed/llamadas.parquet")
    logger.info(f"Dataset cargado. Total llamadas: {len(df_l)}")

    agent = NLPAgent()
    calls_records = df_l.to_dict(orient="records")

    output_json = "outputs/nlp/llamadas_procesadas.json"
    res = agent.process_batch(
        calls_data=calls_records,
        output_path=output_json,
        checkpoint_every=50
    )

    logger.info(f"Procesamiento concluido: {res['total_processed']} llamadas.")

    # Generar perfiles de voz agregados
    logger.info("Generando perfiles agregados de voz del cliente...")
    profile_c3 = get_voice_profile(cluster_id=3, results_path=output_json)
    
    report_path = "outputs/nlp/resumen_voz_cliente.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "cluster_3_profile": profile_c3.model_dump(),
            "summary_comparison": {
                "total_calls": len(df_l),
                "cluster_3_calls": profile_c3.calls_analyzed,
                "top_motivo_cluster_3": profile_c3.motive_distribution[0] if profile_c3.motive_distribution else None,
                "top_submotivo_cluster_3": profile_c3.submotive_distribution[0] if profile_c3.submotive_distribution else None
            }
        }, f, indent=2, ensure_ascii=False)

    logger.info(f"Resumen de voz exportado a {report_path}")

    # Imprimir resumen ejecutivo en consola
    print("\n" + "="*70)
    print("RESUMEN DE VOZ DEL CLIENTE — CLUSTER 3 CRÍTICO")
    print("="*70)
    print(f"Llamadas analizadas en Cluster 3: {profile_c3.calls_analyzed}")
    print("\nDistribución de Motivos Principales:")
    for m in profile_c3.motive_distribution:
        print(f"  - {m['motive']}: {m['count']} ({m['pct']}%)")

    print("\nTop 5 Submotivos Críticos:")
    for sm in profile_c3.submotive_distribution[:5]:
        print(f"  - {sm['submotive']}: {sm['count']} ({sm['pct']}%)")

    print("\nDistribución de Sentimiento:")
    for s, cnt in profile_c3.sentiment_distribution.items():
        print(f"  - {s}: {cnt} ({round(cnt/profile_c3.calls_analyzed*100, 1)}%)")

    print("\nDistribución de Urgencia:")
    for u, cnt in profile_c3.urgency_distribution.items():
        print(f"  - {u}: {cnt} ({round(cnt/profile_c3.calls_analyzed*100, 1)}%)")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
