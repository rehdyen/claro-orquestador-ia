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

## 3. Estructura del Repositorio

```text
.
├── data/                       # Insumos de datos (protegidos bajo .gitignore)
│   ├── raw/                    # Datos crudos locales
│   └── processed/              # Datasets procesados y limpios
├── docs/                       # Blueprints técnicos y arquitectura de referencia
│   ├── databricks_blueprint.md # Diseño Delta Lake, MLflow & Unity Catalog
│   └── data_leakage_audit.md   # Auditoría de variables y T0
├── notebooks/                  # Cuadernos interactivos reproducibles
│   ├── 01_eda_datos.ipynb      # Auditoría exploratoria y distribuciones
│   ├── 02_nlp_llamadas.ipynb   # Procesamiento LLM de las 500 llamadas
│   ├── 03_modelos_ml.ipynb     # Entrenamiento Dual LightGBM, Lift y SHAP
│   └── 04_orquestador_ia.ipynb # Pipeline E2E Multi-Agente con HITL
├── outputs/                    # Artefactos generados exportables
│   ├── figures/                # Gráficos de Lift, Curvas PR/ROC y SHAP
│   ├── models/                 # Modelos entrenados (.joblib / MLflow)
│   ├── nlp/                    # Clasificación estructurada de llamadas (JSON)
│   └── reports/                # Informes ejecutivos y matrices de impacto
├── presentacion/               # Sustentación ejecutiva para la Gerencia
│   └── sustentacion_claro.pptx # Deck ejecutivo de 15 minutos
├── src/                        # Código modular de producción
│   ├── agents/                 # Agentes LangGraph (VoC, Intelligence, Orchestrator)
│   ├── models/                 # Pipelines de entrenamiento e inferencia ML
│   ├── tools/                  # Herramientas Python y servidor FastMCP
│   └── utils/                  # Ingesta, validación y métricas de negocio
├── tests/                      # Suite de pruebas automatizadas (pytest)
├── .gitignore                  # Políticas de exclusión y confidencialidad
├── requirements.txt            # Dependencias reproducibles fijadas
└── README.md                   # Documentación principal del proyecto
```

---

## 4. Instalación y Reproducibilidad

### Prerrequisitos
* Python 3.10 o superior.
* Git y GitHub CLI (`gh`).

### Configuración del Entorno
```bash
# Clonar el repositorio
git clone https://github.com/rehdyen/claro-orquestador-ia.git
cd claro-orquestador-ia

# Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Linux/macOS
# .venv\Scripts\activate   # En Windows PowerShell

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución de Pruebas Unitarias
```bash
pytest tests/ -v
```

---

## 5. Gobernanza y Confidencialidad

Este repositorio implementa controles estrictos de seguridad de la información:
* **Habeas Data & Secreto Comercial:** Ningún dato transaccional real de clientes de Claro Colombia es almacenado ni versionado en este repositorio.
* Los insumos `.xlsx` y `.csv` se encuentran permanentemente ignorados en `.gitignore`.
