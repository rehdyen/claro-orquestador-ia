# Guion de Sustentación Oral y Defensa Técnica (15 Minutos)
**Rol**: Orquestador de Agentes de IA / Machine Learning — Claro Colombia  
**Candidato**: Neydher Antonio Martin Ramos  
**Evaluador Principal**: Rafael José Del Castillo Pavajeau (Gerencia de Analítica Avanzada)  
**Duración Total**: 15 Minutos de Exposición + Sesión de Preguntas y Respuestas (Q&A)  
**Fecha**: Septiembre 2026  

---

## Estructura Temporal de la Presentación

```
[00:00 - 01:00] Slide 1: Apertura Ejecutiva y Declaración de Propósito
[01:00 - 02:30] Slide 2: El Diagnóstico y el Hallazgo Oculto ("Silent Churn Gap")
[02:30 - 04:00] Slide 3: La Voz del Cliente (NLP): Evidencia Estructurada de 500 Llamadas
[04:00 - 05:30] Slide 4: Estrategia Predictiva Dual: Separando Fuga de Intención
[05:30 - 07:30] Slide 5: Rigor Estadístico: Cero Fuga T0 y Lift@10 = 9.05x
[07:30 - 09:00] Slide 6: Explicabilidad: Convergencia de Evidencia (SHAP + Voz del Cliente)
[09:00 - 10:30] Slide 7: Orquestación Multi-Agente: LangGraph con Gobernanza HITL
[10:30 - 11:45] Slide 8: Gobernanza de Acciones: Coherencia Operativa (Falla Técnica != Descuento)
[11:45 - 13:15] Slide 9: Valor Económico: ROI por Decil Empírico y Escenarios de Uplift
[13:15 - 14:15] Slide 10: Productivización: Blueprint Conceptual en Azure Databricks
[14:15 - 15:00] Slide 11: Cierre: Escuchar, Predecir, Explicar, Gobernar y Medir Valor
```

---

## Minuto a Minuto: Guion Verbal

### Minuto 00:00 – 01:00 | Diapositiva 1: Portada y Propósito
**Acción visual**: Mostrar Slide 1 en pantalla completa. Tono seguro, profesional, ritmo pausado y entusiasta.

> *"Muy buenos días, Rafael, y miembros del Comité de Analítica Avanzada de Claro Colombia.  
> Mi nombre es Neydher Antonio Martin Ramos, y hoy vengo a presentarles una solución integral de retención diseñada para el **Cluster 3 de Hogar**, articulando tres pilares: **Machine Learning estadísticamente honesto**, **procesamiento estructurado de la Voz del Cliente** y un **sistema multi-agente gobernado bajo arquitectura Lakehouse**.*  
>
> *Nuestra premisa de trabajo no fue automatizar descuentos indiscriminados, sino construir un sistema capaz de **escuchar, predecir, explicar, orquestar, gobernar y medir valor de negocio**. Entremos de inmediato al diagnóstico."*

---

### Minuto 01:00 – 02:30 | Diapositiva 2: El Diagnóstico y el Silent Churn Gap
**Acción visual**: Pasar a Slide 2. Señalar el contraste 52 / 52.

> *"El Cluster 3 concentra 20.000 clientes residenciales con alta densidad de valor (ARPU promedio de $96.447 COP). Aunque la deserción global parece pequeña —un **0.52% de churn efectivo** (104 bajas)— casi el **20% de la base registra intención de retiro**.*  
>
> *Aquí surge el hallazgo central del caso: el **'Silent Churn Gap'**.  
> Al cruzar ambas variables, encontramos que **exactamente 52 de los 104 desertores reales nunca llamaron ni radicaron intención previa de cancelación**.  
> La implicación de negocio es inmediata: **una estrategia que solo atienda las llamadas de cancelación deja fuera al 50% del churn observado**. Son clientes que sufren degradación del servicio en silencio y migran sin previo aviso.  
> Por esto, **la intención de retiro no puede sustituir al churn real**: se requieren dos modelos especializados para dos rutas de fuga complementarias."*

---

### Minuto 02:30 – 04:00 | Diapositiva 3: La Voz del Cliente (VoC)
**Acción visual**: Pasar a Slide 3. Mostrar el gráfico de barras comparativo de motivos.

> *"Para entender qué experimentan estos clientes, procesamos **500 transcripciones de llamadas reales** mediante un pipeline estructurado de NLP con taxonomía cerrada (6 macro-motivos y 24 sub-motivos) y contratos Pydantic (0 errores de esquema).*  
>
> *Aclaramos una decisión metodológica clave: **la voz del cliente no se cruza 1:1 con el dataset estructurado porque no existe llave de enlace**, sino que se integra rigurosamente a nivel de clúster y arquetipos colectivos.  
> En el Cluster 3, los motivos dominantes son **Precio y Competencia (37.54%)** y **Falla Técnica (24.60%)**. Frente a otros clústeres, este grupo presenta **+4.18 puntos porcentuales en quejas técnicas**, **+7.44 pp en sentimiento negativo** y **+5.09 pp en urgencia crítica**. La insatisfacción técnica es un rasgo distintivo del segmento."*

---

### Minuto 04:00 – 05:30 | Diapositiva 4: Estrategia Predictiva Dual y Control T0
**Acción visual**: Pasar a Slide 4. Comparar las dos tarjetas de modelado.

> *"Diseñamos dos modelos especializados en LightGBM sobre **108 variables predictoras ex-ante**:  
> - **El Modelo A** predice el **Churn Efectivo (BAN_CHURN)** sobre una prevalencia del 0.52%. Emplea árboles compactos regularizados (`max_depth=3`, `num_leaves=7`) y `scale_pos_weight` dinámico para capturar el riesgo sin sobreajustar ruido.  
> - **El Modelo B** anticipa la **Intención de Cancelación (BAN_INTENCION_CANCELACION)** sobre una prevalencia del 19.91%, optimizado para priorizar la atención proactiva en canales de contacto.*  
>
> *Ambos modelos fueron blindados contra fuga temporal ($T_0$): auditamos las 129 variables y excluimos las señales post-tratamiento, como `ESTADO_FUENTE_C` (que tenía correlación artificial de 1.000 por ser la marca de liquidación), `VAL_SALDO_ACTUAL` y las órdenes de desconexión `BAN_OT_CERRADAS_DX`."*

---

### Minuto 05:30 – 07:30 | Diapositiva 5: Rigor Estadístico y Lift@10 = 9.05x
**Acción visual**: Pasar a Slide 5. Resaltar las curvas de Lift y los Intervalos de Confianza al 95%.

> *"En problemas con desbalance severo, el accuracy no tiene sentido: evaluamos la capacidad de ranking.  
> En el conjunto de prueba independiente (Holdout de 4.000 clientes), el **Modelo A alcanza un Lift@10 de 9.048x** con un intervalo de confianza al 95% obtenido por Bootstrap de **[7.62x a 10.00x]**.  
> Esto significa que al contactar al 10% más riesgoso priorizado por el modelo (el Decil 1), **capturamos a más del 90% de todos los clientes que van a desertar**.  
> El PR-AUC se situó en **0.4738** (frente a una línea base de 0.0052) y el ROC-AUC en **0.9569**. En validación cruzada repetida de 20 folds, el desempeño fue consistente (PR-AUC $0.4383 \pm 0.0732$), demostrando estabilidad sin fugas."*

---

### Minuto 07:30 – 09:00 | Diapositiva 6: Explicabilidad y Convergencia de Evidencia
**Acción visual**: Pasar a Slide 6. Mostrar el gráfico SHAP Beeswarm.

> *"Para interpretar los modelos, utilizamos **SHAP TreeExplainer**.  
> Es fundamental enfatizar nuestro rigor técnico: **SHAP explica el comportamiento asociativo del modelo, no demuestra causalidad**.  
> Sin embargo, observamos una **convergencia temática contundente entre las señales estructuradas y la Voz del Cliente**:  
> Los principales drivers del Modelo A son `VAL_RECLAMOS_MES`, `VELOCIDAD_INTERNET_MBPS`, `VAL_RENTA_ACTUAL` y `VAL_VAR_RENTA`.  
> Esto converge directamente con lo reportado en las llamadas: clientes en planes de baja velocidad, con quejas acumuladas y shocks tarifarios. Aunque no se unen 1:1, ambas fuentes apuntan a las mismas dimensiones críticas de fricción."*

---

### Minuto 09:00 – 10:30 | Diapositiva 7: Orquestación Multi-Agente en LangGraph
**Acción visual**: Pasar a Slide 7. Explicar el flujo de nodos y compuertas HITL.

> *"Para convertir estas predicciones en acciones gobernadas, implementamos un sistema multi-agente en **LangGraph**:  
> 1. En ramas paralelas, el **Customer Intelligence Agent** y el **VoC Agent** consumen los activos analíticos precalculados (scores, deciles y resumen de voz).  
> 2. El **Retention Orchestrator** consulta el catálogo oficial de acciones y evalúa el impacto financiero.  
> 3. Un **Judge Agent determinístico** audita la propuesta contra las restricciones corporativas, con un ciclo de reintento acotado a 1 loop.  
> 4. El sistema incorpora **Human-in-the-Loop nativo mediante la función `interrupt()`**: si la acción involucra impacto financiero, si el cliente es VIP ($ARPU \ge \$109.840$ COP), o si se detecta Silent Churn, el flujo se suspende y envía el caso a la bandeja del supervisor humano en Claro."*

---

### Minuto 10:30 – 11:45 | Diapositiva 8: Gobernanza de Acciones y Coherencia Operativa
**Acción visual**: Pasar a Slide 8. Explicar el principio: "Falla técnica no es igual a rebaja comercial".

> *"Nuestra gobernanza establece una regla no negociable: **Falla técnica $\neq$ Rebaja comercial automática**.  
> Si un cliente tiene fallas físicas de internet, darle un descuento temporal no resuelve el problema; el cliente sufrirá la misma intermitencia y desertará dos meses después con un menor margen para Claro.  
> Por ello:  
> - Ante averías de red o reclamos activos, prescribimos **`PRIORITY_TECH_VISIT`** ($35.000 COP) para certificar acometida y módem.  
> - Si la lentitud es por plan bajo ($\le 50$ Mbps) sin avería, prescribimos **`SPEED_UPGRADE`** ($15.000 COP).  
> - El descuento tarifario (**`TEMP_RENT_DISCOUNT`**) se limita a un **máximo estándar de 2 meses** para alivio tarifario; periodos de 3 meses exigen Senior Review.  
> - Y para el Silent Churn, disparamos **`PREVENTIVE_DIAGNOSTIC`** ($8.000 COP) para auditar satisfacción antes de la baja."*

---

### Minuto 11:45 – 13:15 | Diapositiva 9: Valor Económico y Escenarios de ROI
**Acción visual**: Pasar a Slide 9. Resaltar la tabla de triaje selectivo.

> *"En la evaluación financiera, adoptamos un principio de estricta honestidad: **no utilizamos las probabilidades brutas de LightGBM para calcular el ROI**, ya que el weighting distorsiona la calibración. Utilizamos la **tasa empírica observada en el Decil 1 (5.19%)**.*  
>
> *En los 2.000 clientes del Decil 1, hay 104 desertores esperados (~$120.1M COP en riesgo anual).  
> Si se interviniera masivamente a los 2.000 clientes a $28.000 COP promedio ($56M COP de costo), la campaña sería deficitaria.  
> Por eso, el orquestador aplica **Triaje Selectivo sobre el Top 500 de mayor riesgo**:  
> Con un costo promedio de $12.500 COP (inversión de $6.25M COP):  
> - En el **Escenario Base (20% de uplift)**: se salvan **13.5 clientes**, protegiendo **$15.62M COP** brutos anuales, logrando un **beneficio neto de +$9.37M COP**, un **Benefit/Cost Ratio de 2.50x** y un **Net ROI de +1.50x (+150%)**.  
> - Incluso en el **Escenario Conservador (10% de uplift)**: se salvan **6.8 clientes**, protegiendo **$7.81M COP**, con beneficio neto positivo de **+$1.56M COP** y **Benefit/Cost de 1.25x**."*

---

### Minuto 13:15 – 14:15 | Diapositiva 10: Productivización en Azure Databricks
**Acción visual**: Pasar a Slide 10. Recorrer los componentes del blueprint conceptual.

> *"Para escalar esta solución, diseñamos un **Blueprint Conceptual de Productivización en Azure Databricks**:  
> - **Delta Lake Medallion**: Ingesta con Auto Loader en Bronze, curaduría con Delta Live Tables y Feature Store libre de fugas T0 en Silver, y publicación de scores y bitácora HITL en Gold.  
> - **MLflow Model Registry & Unity Catalog**: Firmas estrictas de modelos, linaje de datos de extremo a extremo y diseño compatible con principios de protección de datos personales de Colombia (Ley 1581), sujeto a validación legal.  
> - **Databricks Workflows**: Un DAG batch de ejemplo (ej. 02:00 AM) para calificar a millones de clientes en Spark.  
> - **Data Quality Monitoring / Data Profiling**: Alertas preventivas configurables de Data Drift (ej. PSI > 0.15) sobre drivers SHAP clave y seguimiento mensual de Concept Drift."*

---

### Minuto 14:15 – 15:00 | Diapositiva 11: Cierre Ejecutivo
**Acción visual**: Pasar a Slide 11. Cierre convincente y seguro.

> *"En conclusión:  
> Entregamos una solución que **escucha la voz del cliente**, **predice con Lift de 9x sin fugas T0**, **explica el comportamiento del modelo**, **orquesta intervenciones con coherencia operativa**, **gobierna el riesgo financiero con supervisión humana**, y **mide el valor económico con rigor matemático**.  
>
> Todo el paquete está respaldado por 23 pruebas unitarias automatizadas en verde y un repositorio público auditable.  
> Muchas gracias, y quedo a su entera disposición para sus preguntas."*

---

## Banco de Preguntas Difíciles & Respuestas Maestras (Q&A con Rafael Del Castillo)

### 1. "¿Cómo confías en un Lift de 9x con sólo 104 churners?"
> *"Por tres controles metodológicos independientes:  
> 1. **Validación Cruzada Repetida**: Evaluamos 20 particiones estratificadas independientes (4 folds x 5 repeats), obteniendo un Lift@10 promedio de $8.31 \pm 0.80x$ y PR-AUC de $0.438 \pm 0.073$, confirmando estabilidad.  
> 2. **Holdout Blindado e Intervalos Bootstrap**: En el 20% de holdout final, el Lift@10 puntual fue de 9.048x, y su intervalo al 95% por bootstrap se situó entre 7.62x y 10.00x.  
> 3. **Auditoría Red Team de Leakage**: Ejecutamos una prueba de permutación de etiquetas donde el Lift colapsó a 0.48x y el PR-AUC a 0.0036, y un challenger sin las 3 variables principales que mantuvo un Lift de 8.57x. Esto demuestra que el desempeño es genuino y no producto de memorización ni de un proxy aislado."*

### 2. "¿Por qué dos modelos y no uno solo?"
> *"Porque 104 churners observados se dividen exactamente en **52 con intención previa y 52 sin intención (Silent Churn)**. Son dos fenómenos con dinámicas distintas: la intención es una señal reactiva de alta frecuencia (20% prevalencia) para atención temprana en canales; el churn efectivo es un evento terminal de desconexión (0.52%) que suele ocurrir en silencio por fatiga técnica. Un modelo único de churn diluiría la señal de intención, y un modelo único de intención ignoraría al 50% de las bajas reales."*

### 3. "¿Para qué un sistema multi-agente si ya tenemos los modelos de Machine Learning?"
> *"Los modelos predicen probabilidades; los agentes gobiernan cómo convertir esa evidencia en decisiones de negocio. Un modelo de ML no sabe si un cliente tiene un reclamo técnico pendiente, si el descuento solicitado supera el límite presupuestal o si la cuadrilla técnica debe despacharse en menos de 24 horas. El sistema multi-agente integra la evidencia estructurada con la no estructurada, aplica las políticas corporativas y activa el control humano cuando está en juego el margen de la compañía."*

### 4. "¿SHAP prueba causalidad entre las variables y la deserción?"
> *"No. SHAP mide la contribución marginal de cada variable a la predicción del modelo basada en valores de Shapley de teoría de juegos; no es una prueba de inferencia causal. Lo que afirmamos técnicamente es una **convergencia temática de evidencia**: las variables con mayor peso en el modelo (`VAL_RECLAMOS_MES`, `VELOCIDAD`) concuerdan con los problemas que los clientes expresan en la voz cualitativa (fallas de internet y lentitud), permitiéndonos construir hipótesis operativas sólidas para guiar las acciones."*

### 5. "¿Por qué no cruzaron las llamadas con los clientes a nivel 1:1?"
> *"Porque en los insumos entregados no existe una llave de cuenta o cédula común. Cualquier intento de hacer un join sintético o artificial falsearía los datos e induciría sesgos graves en la evaluación. Preservamos la integridad analítica triangulando las fuentes a nivel de clúster y arquetipos de comportamiento, lo cual es la mejor práctica cuando no se cuenta con identificador unívoco."*

### 6. "¿Por qué no utilizar las probabilidades crudas del modelo para proyectar el ROI?"
> *"Porque al entrenar con `scale_pos_weight` para contrarrestar el desbalance severo (0.52%), las probabilidades predichas se desplazan hacia arriba y pierden calibración directa. Si multiplicáramos el ARPU por una probabilidad no calibrada de 0.60, inflaríamos ficticiamente los ahorros del proyecto. En su lugar, utilizamos la **tasa empírica observada en el Decil 1 (5.19%)**, lo que garantiza que las proyecciones financieras sean matemáticamente auditables y veraces."*

### 7. "¿Qué parte de la solución está productiva hoy?"
> *"El blueprint de Azure Databricks es una propuesta conceptual de arquitectura de productivización. Lo que sí está plenamente implementado, probado y funcional hoy es el **núcleo analítico del assessment**: el pipeline de NLP con Pydantic, los modelos predictivos duales, el motor de explicabilidad SHAP, el grafo de agentes en LangGraph con compuertas HITL y el servidor FastMCP, todo validado localmente con 23 pruebas automatizadas pasando."*
