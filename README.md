# Claro Colombia — Orquestador de Agentes de IA & Machine Learning

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Architecture](https://img.shields.io/badge/Architecture-LangGraph%20%7C%20FastMCP-orange.svg)]()
[![ML Framework](https://img.shields.io/badge/ML-LightGBM%20%7C%20SHAP-green.svg)]()
[![Target](https://img.shields.io/badge/Target-Cluster%203%20Churn%20Mitigation-red.svg)]()

> **Prueba Técnica de Selección:** Orquestador de Agentes de IA / Machine Learning  
> **Candidato:** Neydher Antonio Martin Ramos  
> **Evaluador / Liderazgo:** Rafael José Del Castillo Pavajeau — Gerencia de Analítica Avanzada, Claro Colombia  

---

## 1. Visión Ejecutiva y Propósito de Negocio

El **Cluster 3** representa el segmento de clientes residenciales más vulnerable a la deserción (*churn*) y deterioro de ingresos (*ARPU*) dentro de Claro Colombia. Este proyecto implementa una solución integral de grado de producción que orquesta modelos predictivos de Machine Learning, Procesamiento de Lenguaje Natural (NLP) sobre la Voz del Cliente (500 llamadas transcritas) y un sistema Multi-Agente con compuertas de supervisión humana (**Human-in-the-Loop - HITL**).

```text
    ┌────────────────────────────────────────────────────────┐
    │           Voz del Cliente (500 Transcripciones)        │
    │                      +                                 │
    │        20.000 Registros Estructurados (Cluster 3)      │
    └──────────────────────────┬─────────────────────────────┘
                               │
                               ▼
    ┌────────────────────────────────────────────────────────┐
    │       Auditoría de Datos, T0 & Feature Engineering     │
    └──────────────────────────┬─────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌───────────────────────────┐         ┌───────────────────────────┐
│     NLP / VoC Agent       │         │ Customer Intelligence     │
│ (Motivo, Submotivo,       │         │ (LightGBM Churn/Intención │
│  Sentimiento, Urgencia)   │         │  + SHAP Tree Explainers)  │
└─────────────┬─────────────┘         └─────────────┬─────────────┘
              │                                     │
              └──────────────────┬──────────────────┘
                                 │
                                 ▼
              ┌─────────────────────────────────────┐
              │    Retention Orchestrator Agent     │
              │  (Evaluación de Catálogo y ROI)     │
              └──────────────────┬──────────────────┘
                                 │
                       ┌─────────┴─────────┐
                       ▼                   ▼
           [Riesgo Alto / VIP]     [Riesgo Operativo]
                   │                       │
                   ▼                       ▼
            Human-in-the-Loop      Acción Automática
            (Aprobación Humana)    (Autogestión / Red)
```

---

## 2. Decisiones Arquitectónicas Fundamentales

1. **Restricción Crítica de Integración (No Cruce 1:1 Forzado):**
   * El dataset `Clientes_Cluster_3.xlsx` (20.000 filas × 129 columnas) carece de identificadores de cuenta (`CUENTA`) o cliente (`DOCUMENTO`).
   * Las llamadas (`Llamadas.xlsx`, 500 registros) se integran estrictamente a nivel de **Cluster / Arquetipo colectivo**, garantizando rigurosidad estadística sin falsear uniones individuales.
2. **Estrategia Dual de Machine Learning (LightGBM):**
   * **Modelo A (Churn Efectivo):** Target `BAN_CHURN` (severamente desbalanceado ~0.54%). Optimizado vía PR-AUC, `scale_pos_weight` y evaluado en Lift@10 y Lift@20.
   * **Modelo B (Intención Temprana de Cancelación):** Target `BAN_INTENCION_CANCELACION` (~20.22%). Permite intervención proactiva antes de que el daño sea irreversible.
3. **Control Estricto de Fuga de Datos (*Data Leakage* / T0):**
   * Exclusión metódica de variables post-evento o contaminadas para evitar sobreajuste engañoso.
4. **Sistema Multi-Agente con LangGraph & FastMCP:**
   * Orquestación stateful basada en grafos con persistencia y pausa (`interrupt()`) para autorizaciones comerciales en clientes de alto valor.

---

## 3. Estructura del Repositorio y Entregables

```text
.
├── data/                       # Insumos y datos procesados (protegidos bajo .gitignore)
│   ├── processed/              # Taxonomía congelada, particiones y datos procesados
│   │   └── taxonomy_v1.json    # Taxonomía NLP oficial (6 macro-motivos, 24 sub-motivos)
│   └── raw/                    # Datos crudos (.gitkeep)
├── docs/                       # Blueprints técnicos y gobernanza
│   ├── databricks_blueprint.md # Blueprint empresarial Azure Databricks Lakehouse
│   ├── data_leakage_t0_audit.md# Auditoría formal de control de fuga T0
│   ├── feature_audit.csv       # Clasificación de 129 variables por rol
│   └── matriz_accionables_roi.md # Matriz Impacto vs Esfuerzo y ROI empírico
├── outputs/                    # Artefactos analíticos y modelos exportables
│   ├── figures/                # Curvas Lift/PR, contrates NLP y Beeswarm SHAP
│   ├── models/                 # Modelos entrenados (.joblib) y métricas (.json)
│   └── nlp/                    # Llamadas procesadas y resumen de voz del cliente
├── presentacion/               # Sustentación ejecutiva para Claro Colombia
│   ├── guion_defensa_15min.md  # Guion oral palabra por palabra (15 min) + Banco Q&A
│   └── sustentacion_claro.pptx # Deck ejecutivo de 11 diapositivas en 16:9 (python-pptx)
├── src/                        # Código modular de producción
│   ├── agents/                 # Agentes LangGraph (Customer, VoC, Orchestrator, Judge, Graph)
│   ├── models/                 # Pipelines de entrenamiento dual, métricas y SHAP
│   ├── pipelines/              # Procesamiento batch NLP y generador de presentación
│   └── tools/                  # Catálogo de acciones, FastMCP y analítica de clientes
├── tests/                      # Suite automatizada de pruebas (21/21 PASS)
│   ├── test_catalog_roi.py     # Tests de catálogo y cálculo económico empírico
│   ├── test_models.py          # Tests de inferencia de modelos e integridad de métricas
│   ├── test_multiagent_scenarios.py # 8 escenarios de gobernanza, HITL y restricciones
│   └── test_nlp_agent.py       # Tests de taxonomía y contratos Pydantic
├── requirements.txt            # Dependencias reproducibles fijadas
└── README.md                   # Documentación principal del proyecto
```

---

## 4. Estado de los Gates de Entrega (Definition of Done)

| Gate | Nombre | Estado | Criterios Validados |
| :--- | :--- | :---: | :--- |
| **G0** | **Data & Plan Ready** | **PASS** | Auditoría de 129 columnas, categorización estricta de roles, congelamiento de política T0. |
| **G1** | **Voice & Data Ready** | **PASS** | 500 llamadas procesadas (0 fallos de esquema Pydantic), taxonomía 6x24, contraste Cluster 3. |
| **G2** | **Predictive Ready** | **PASS** | Modelos Duales LightGBM. Modelo A: **Lift@10 = 9.05x** (IC 95%: [7.62 - 10.00x]), PR-AUC = 0.4738. Modelo B: Lift@10 = 3.81x, PR-AUC = 0.6278. 20-fold CV y SHAP TreeExplainer. |
| **G3** | **Agentic Ready** | **PASS** | LangGraph StateGraph paralelo con reducers, detección de Silent Churn, Judge determinístico, **HITL nativo vía `interrupt()`** y servidor FastMCP. |
| **G4** | **Business & Delivery Ready** | **PASS** | ROI basado en tasa empírica por decil (5.19%), 3 escenarios de retención incremental (10%, 20%, 30%), Blueprint Azure Databricks, Deck PPTX de 11 slides y guion de defensa de 15 min. |

---

## 5. Instalación y Reproducibilidad

### Configuración del Entorno
```bash
# Clonar repositorio
git clone https://github.com/rehdyen/claro-orquestador-ia.git
cd claro-orquestador-ia

# Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Linux/macOS
# .venv\Scripts\activate   # En Windows PowerShell

# Instalar dependencias fijadas
pip install -r requirements.txt
```

### Ejecución de Pruebas Unitarias (21 Tests en Verde)
```bash
python -m pytest -v
```

### Generación Automatizada de la Presentación Ejecutiva
```bash
python src/pipelines/generate_presentation.py
```

---

## 6. Gobernanza y Confidencialidad

Este repositorio implementa controles estrictos de seguridad de la información:
* **Habeas Data & Secreto Comercial (Ley 1581 Colombia):** Ningún dato transaccional real, número telefónico ni PII de clientes de Claro Colombia es almacenado ni versionado en este repositorio.
* Los insumos `.xlsx`, `.parquet` y `.env` se encuentran permanentemente ignorados en `.gitignore`.
