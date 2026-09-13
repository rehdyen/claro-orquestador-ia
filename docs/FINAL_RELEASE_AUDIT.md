# Final Release Audit
**Proyecto**: Orquestador de Agentes de IA / Machine Learning — Retención Hogar Cluster 3  
**Compañía**: Claro Colombia — Gerencia de Analítica Avanzada  
**Evaluador Líder**: Rafael José Del Castillo Pavajeau  
**Candidato / Orquestador Principal**: Neydher Antonio Martin Ramos (`rehdyen`)  
**Fecha de Cierre**: Septiembre 2026  
**Repositorio Oficial**: [https://github.com/rehdyen/claro-orquestador-ia](https://github.com/rehdyen/claro-orquestador-ia) (Público)  

---

## Commit
`docs(release)`: publication-ready executive blueprints, vector diagrams, and delivery package (Release Oficial en master).

## Gates
- **G0 (Data & Plan Ready)**: **PASS**
- **G1 (Voice & Data Ready)**: **PASS**
- **G2 (Predictive Ready)**: **PASS**
- **G3 (Agentic Ready)**: **PASS**
- **G4 (Business & Delivery Ready)**: **PASS**

---

## Tests
- **23/23 PASS** (`pytest -v` en 4.72s, 0 errores, 0 fallos).
  - `tests/test_catalog_roi.py`: 3/3 PASS (Catálogo, ROI empírico por decil, proyección de portafolio).
  - `tests/test_models.py`: 5/5 PASS (Inferencia A/B, cálculo Lift@10, integridad de métricas).
  - `tests/test_multiagent_scenarios.py`: 10/10 PASS (Falla técnica, presión de precio, cliente VIP, Silent Churn, techo de descuento 20%, acción fuera de catálogo, abstención de bajo riesgo, bloqueo de join forzado 1:1, alcanzabilidad de `SPEED_UPGRADE` y alineación de duración de descuento a 2 meses).
  - `tests/test_nlp_agent.py`: 5/5 PASS (Taxonomía congelada 6x24, contratos Pydantic, extracción de entidades y abstención).

---

## Data Leakage (Auditoría Red Team)
- **Estado**: **PASS**
- **Hallazgos**:
  - Exclusión confirmada en $T_0$ de 8 variables contaminadas: `ESTADO_FUENTE_C` (correlación 1.000 con target por ser marca de liquidación), `VAL_SALDO_ACTUAL` (saldo llevado a 0.0), `BAN_OT_CERRADAS_DX` (orden de desconexión ejecutada), y variables de motivos/intenciones/reincidencias.
  - **Prueba de Permutación de Etiquetas**: Al barajar aleatoriamente el target en entrenamiento, en holdout el PR-AUC colapsó de 0.4738 a **0.0036** (esperado ~0.0053), el Lift@10 a **0.476x** (esperado ~1.00x) y el ROC-AUC a **0.2863**, confirmando que el pipeline no aprende relaciones espurias.
  - **Challenger sin Top 3 Dominantes**: Al entrenar sin `VAL_RECLAMOS_MES`, `VELOCIDAD_INTERNET_MBPS` y `VAL_RENTA_ACTUAL`, el modelo retiene un Lift@10 de **8.571x** y ROC-AUC de **0.9517**, demostrando que la señal está distribuida de forma robusta en las 105 variables restantes.

---

## Confidentiality Public Repo
- **Estado**: **PASS**
- **Hallazgos**:
  - Auditoría exhaustiva del working tree y del historial completo de Git (todos los commits).
  - Ausencia confirmada de: `Clientes_Cluster_3.xlsx`, `Llamadas.xlsx`, `Diccionario_Datos_Cluster3.xlsx`, archivos `.parquet`, `.env`, tokens GitHub, API keys, contraseñas y datos con PII de clientes.
  - Los únicos artefactos de datos versionados son salidas anonimizadas requeridas por la prueba (`outputs/nlp/llamadas_procesadas.json` con tokens `[NOMBRE]`), metadata (`docs/feature_audit.csv`) y modelos entrenados.

---

## Model A — Churn Efectivo (`BAN_CHURN`)
- **Prevalencia**: 0.52% (104 desertores en 20.000 clientes).
- **Holdout Test (4.000 clientes)**:
  - **Lift@10**: **9.048x** (IC 95% Bootstrap: [7.619x - 10.000x])
  - **Lift@20**: **4.762x** (IC 95% Bootstrap: [4.048x - 5.000x])
  - **PR-AUC**: **0.4738** (IC 95% Bootstrap: [0.2832 - 0.6824]; línea base azar: 0.00525)
  - **ROC-AUC**: **0.9569** (IC 95% Bootstrap: [0.9072 - 0.9903])
  - **Brier Score**: **0.0092**
- **Validación Cruzada (Repeated Stratified K-Fold, 20 evaluaciones)**:
  - PR-AUC: $0.4383 \pm 0.0732$
  - Lift@10: $8.311 \pm 0.796x$
  - ROC-AUC: $0.9504 \pm 0.0228$
- **Top Drivers SHAP**: `VAL_RECLAMOS_MES`, `VELOCIDAD_INTERNET_MBPS`, `VAL_RENTA_ACTUAL`, `VAL_SUM_VAL_MINUTOS_VOZ`, `VAL_VAR_RENTA`.

---

## Model B — Intención de Cancelación (`BAN_INTENCION_CANCELACION`)
- **Prevalencia**: 19.91% (3.981 clientes con intención en 20.000 clientes).
- **Holdout Test (4.000 clientes)**:
  - **Lift@10**: **3.812x** (IC 95% Bootstrap: [3.603x - 4.034x])
  - **Lift@20**: **2.892x** (IC 95% Bootstrap: [2.735x - 3.022x])
  - **PR-AUC**: **0.6278** (IC 95% Bootstrap: [0.5986 - 0.6578]; línea base azar: 0.1991)
  - **ROC-AUC**: **0.8248** (IC 95% Bootstrap: [0.8085 - 0.8420])
  - **Brier Score**: **0.1501**
- **Validación Cruzada (Stratified 5-Fold)**:
  - PR-AUC: $0.6093 \pm 0.0139$
  - Lift@10: $3.639 \pm 0.1566x$
  - ROC-AUC: $0.8024 \pm 0.0101$
- **Top Drivers SHAP**: `VAL_LLAM_ADTIVAS_NEUTRAS`, `BAN_CAMPANA_VENTA`, `VAL_VAR_RENTA`, `BAN_CAZA_OFERTA`.

---

## NLP / Voz del Cliente (VoC)
- **Volumen**: 500 llamadas procesadas de extremo a extremo (0 errores Pydantic).
- **Taxonomía Congelada**: 6 macro-motivos y 24 sub-motivos (`taxonomy_v1.json`).
- **Distribución de Motivos en Cluster 3**:
  - Precio y Competencia: **37.54%**
  - Falla Técnica: **24.60%**
  - Mudanza y Traslado: **19.09%**
  - UNRESOLVED: **9.39%**
  - Facturación y Cobros: **8.74%**
  - Otros: **0.65%**
- **Contraste vs. Otros Clústeres**:
  - Falla Técnica: **+4.18 pp**
  - Sentimiento Negativo: **+7.44 pp**
  - Urgencia Crítica: **+5.09 pp**
- **Integración**: No se fuerza cruce 1:1 por ausencia de identificador; se triangula a nivel de clúster y arquetipos colectivos.

---

## Agent Governance & Multi-Agente
- **Orquestación**: Grafo dirigido acíclico en **LangGraph** con estado tipado (`OrchestratorState`), ejecución paralela de ramas (`CustomerIntelligence` y `VoCAgent`) y reducción con operadores `add`.
- **Detección de Patrones**: Flag determinístico de `SILENT_CHURN_PATTERN` (Decil 1 Churn + Decil $\ge 6$ Intención).
- **Compuertas Human-in-the-Loop (HITL)**:
  - Implementación nativa con `interrupt()` y checkpointer en memoria persistente.
  - Reglas de activación: acciones financieras (descuentos), contractuales (upgrade de velocidad), clientes VIP ($ARPU \ge \$109.840$ COP) en deciles 1-2, patrón Silent Churn, descuento $> 20\%$ (Senior Review), duración $> 2$ meses (Senior Review) o acción fuera de catálogo.
- **Interoperabilidad**: Servidor y cliente **FastMCP** exponiendo catálogo, puntuación de clientes y resumen de voz del cliente.

---

## Modelo Financiero y ROI

### Fórmulas Auditadas
$$\text{ExpectedAvoidedChurn} = N_{\text{target}} \times \text{empirical\_churn\_rate} \times \text{intervention\_uplift}$$
$$\text{ProtectedRevenue} = \text{ExpectedAvoidedChurn} \times \text{ARPU\_monthly} \times 12$$
$$\text{BenefitCostRatio} = \frac{\text{ProtectedRevenue}}{\text{CampaignCost}}$$
$$\text{NetROI} = \frac{\text{ProtectedRevenue} - \text{CampaignCost}}{\text{CampaignCost}} = \text{BenefitCostRatio} - 1$$

### Supuestos Base
- Universo Total Cluster 3: 20.000 clientes.
- Universo Decil 1: 2.000 clientes (10% superior).
- ARPU Promedio: $96.446,78 COP / mes ($1.157.361 COP anual por cliente).
- Tasa Empírica de Churn en Decil 1: **5.19%** (103.8 desertores naturales esperados; ~$120.1M COP anuales en riesgo).

### Resultado Definitivo: Triaje Selectivo Top 500 (Estrategia Recomendada)
*Población objetivo: 500 clientes con mayor severidad (~65% de churners = 67.5 casos). Costo promedio de contacto ponderado: $12.500 COP $\rightarrow$ Inversión de Campaña: **$6.250.000 COP**.*

| Escenario | Uplift | Clientes Salvados | Protected Revenue | Campaign Cost | Beneficio Neto | Benefit/Cost | Net ROI (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Conservador** | 10.0% | 6.8 | $7.812.189 COP | $6.250.000 COP | +$1.562.189 COP | **1.25x** | **+25.0%** |
| **Base** | 20.0% | 13.5 | $15.624.378 COP | $6.250.000 COP | **+$9.374.378 COP** | **2.50x** | **+1.50x (+150.0%)** |
| **Optimista** | 30.0% | 20.2 | $23.436.568 COP | $6.250.000 COP | +$17.186.568 COP | **3.75x** | **+2.75x (+275.0%)** |

---

## Deliverables (Lista Completa)
1. **Presentación Canónica**: `presentacion/sustentacion_claro.pptx` (11 diapositivas en formato 16:9).
2. **Guion Oral y Q&A**: `presentacion/guion_defensa_15min.md` (Minuto a minuto 0:00 a 15:00 con 7 preguntas difíciles preparadas).
3. **Matriz de Accionabilidad y ROI**: `docs/matriz_accionables_roi.md` + `docs/matriz_accionables_roi.pdf` (versión ejecutiva 16:9).
4. **Blueprint Conceptual Azure Databricks**: `docs/databricks_blueprint.md` + `docs/databricks_blueprint.pdf` (versión ejecutiva 16:9).
5. **Auditoría Red Team de Leakage**: `docs/model_a_leakage_redteam.md`.
6. **Suite de Pruebas Automatizadas**: 23 tests en `tests/`.
7. **Documentación de Proyecto**: `README.md` y `docs/feature_audit.csv`.

---

## Known Limitations
1. **Datos de Corte Transversal (Cross-Sectional Snapshot)**: El dataset estructurado corresponde a un único periodo (`PERIODO = 202508`), impidiendo una partición por series de tiempo hacia el futuro. Esto se mitigó mediante validación cruzada estratificada repetida de 20 folds y holdout ciego con bootstrap.
2. **Desacoplamiento Estructurado vs. Voz**: No existe llave unívoca (`CUENTA`/`DOCUMENTO`) entre las 500 llamadas y los 20.000 registros, por lo que la integración se mantiene honestamente a nivel de clúster y arquetipos.
3. **Blueprint Conceptual**: La infraestructura en Azure Databricks está diseñada formalmente pero no desplegada en nube física de Claro (según el alcance estipulado en la prueba técnica).

---

## Final Status
# **READY FOR SUBMISSION**
Release completamente verificada, auditable, reproducible y alineada entre código, documentación, presentación y correo.
