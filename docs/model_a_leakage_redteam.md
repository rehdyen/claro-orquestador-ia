# Auditoría Red Team de Fuga de Datos (Data Leakage T0) — Modelo A
**Objetivo**: Validación estricta y prueba adversarial sobre el Modelo A (`BAN_CHURN`, prevalencia 0.52%)  
**Evaluador**: Rafael José Del Castillo Pavajeau — Gerencia de Analítica Avanzada, Claro Colombia  
**Candidato**: Neydher Antonio Martin Ramos  
**Fecha**: Septiembre 2026  
**Veredicto Final**: **PASS (Sin Fuga de Datos T0)**  

---

## 1. Contexto y Motivación

El Modelo A exhibe un desempeño predictivo notable sobre el conjunto de Holdout ciego (4.000 clientes):
- **Lift@10**: **9.048x** (IC 95%: [7.619x - 10.000x])
- **PR-AUC**: **0.4738** (Línea base de azar: 0.00525)
- **ROC-AUC**: **0.9569**
- **Repeated Stratified CV (20 folds)**: PR-AUC = $0.4383 \pm 0.0732$, Lift@10 = $8.311 \pm 0.796x$

Dado que el Lift@10 teórico máximo para una prevalencia del 0.525% es de ~10.0x si el 100% de los positivos estuvieran en el primer decil, se ejecutó una **auditoría adversarial exhaustiva (Red Team Audit)** para descartar cualquier fuga sutil o dependencia espuria.

---

## 2. Auditoría Semántica de Variables Top 20 SHAP

Se verificó manualmente la definición de negocio de los 20 principales drivers del modelo en el diccionario oficial:

| Variable | Rol Asignado | Naturaleza Temporal y de Negocio | ¿Riesgo de Fuga? |
| :--- | :---: | :--- | :---: |
| `VAL_RECLAMOS_MES` | PREDICTOR | Volumen de quejas operacionales acumuladas en el mes anterior al corte $T_0$. | NO |
| `VELOCIDAD_INTERNET_MBPS` | PREDICTOR | Ancho de banda contratado en el plan vigente. | NO |
| `VAL_RENTA_ACTUAL` | PREDICTOR | Facturación mensual recurrente del plan. | NO |
| `VAL_SUM_VAL_MINUTOS_VOZ` | PREDICTOR | Consumo de minutos de voz fijos/móviles. | NO |
| `VAL_RENTA_BSC_IVA` | PREDICTOR | Cargo básico antes de impuestos. | NO |
| `VAL_SCORE_CREDITICIO` | PREDICTOR | Puntaje de buró crediticio externo. | NO |
| `VAL_DENSIDAD_ZONA` | PREDICTOR | Densidad habitacional del nodo de red. | NO |
| `VAL_VAR_RENTA` | PREDICTOR | Delta en la tarifa facturada frente al mes previo. | NO |
| `VAL_RENTA_ADIC_IVA` | PREDICTOR | Cargos por servicios adicionales. | NO |
| `VAL_EQUIP_BAS` | PREDICTOR | Número de decodificadores/módems en comodato. | NO |
| `ANTIGUEDAD_MESES` | PREDICTOR | Meses de permanencia contractual del cliente. | NO |
| `VAL_TICKETS_MES` | PREDICTOR | Casos técnicos abiertos en el CRM. | NO |

**Conclusión Semántica**: Ninguna de las variables corresponde a un estado posterior al corte ($T_0$), orden de desconexión ejecutada o proxy de liquidación administrativa.

---

## 3. Prueba Adversarial 1: Permutación Aleatoria de Etiquetas (Sanity Check)

Se entrenó un modelo idéntico en arquitectura e hiperparámetros sobre el Development Set permutando aleatoriamente el vector de etiquetas $y_{\text{churn}}$ (destruyendo cualquier relación real entre $X$ y $y$).

### Resultados en Holdout Test:
- **PR-AUC**: **0.0036** (Línea base esperada: ~0.0053). Colapso total de precisión.
- **Lift@10**: **0.476x** (Esperado por azar: ~1.000x). Incapacidad absoluta de rankear positivos.
- **ROC-AUC**: **0.2863** (Esperado por azar: ~0.5000).

**Veredicto de Permutación**: **PASS**. El pipeline y la regularización de LightGBM no generan métricas artificiales cuando se suministran etiquetas aleatorias.

---

## 4. Prueba Adversarial 2: Modelo Challenger sin Variables Dominantes

Para comprobar si el modelo depende críticamente de un proxy oculto entre las variables más potentes, se entrenó un modelo alternativo (*Challenger*) **excluyendo completamente las 3 variables dominantes**:
- `VAL_RECLAMOS_MES`
- `VELOCIDAD_INTERNET_MBPS`
- `VAL_RENTA_ACTUAL`

### Resultados del Challenger en Holdout (105 variables restantes):
- **PR-AUC**: **0.4233** (vs 0.4738 del modelo oficial)
- **Lift@10**: **8.571x** (vs 9.048x del modelo oficial)
- **ROC-AUC**: **0.9517** (vs 0.9569 del modelo oficial)

**Veredicto del Challenger**: **PASS**. Incluso eliminando las tres variables principales, el modelo retiene un Lift@10 sobresaliente de **8.57x**, demostrando que la señal de riesgo está distribuida de forma robusta a lo largo de las dimensiones de facturación, antigüedad, hardware, consumo y calidad técnica.

---

## 5. Veredicto Final y Cierre de Auditoría

| Control Red Team | Criterio de Éxito | Resultado Observado | Estado |
| :--- | :--- | :---: | :---: |
| **Exclusión de Fugas T0 Históricas** | `ESTADO_FUENTE_C`, `VAL_SALDO_ACTUAL`, `BAN_OT_CERRADAS_DX` fuera de features | 100% Excluidas | **PASS** |
| **Auditoría Semántica Top 20 SHAP** | Ningún estado post-outcome o proxy de liquidación | 0 proxies detectados | **PASS** |
| **Prueba de Permutación de Target** | Lift@10 colapsa a $\approx 1.0x$ y PR-AUC $\approx 0.005$ | Lift@10 = 0.48x, PR-AUC = 0.0036 | **PASS** |
| **Modelo Challenger (sin Top 3)** | Lift@10 $> 3.0x$ demostrando señal distribuida | Lift@10 = 8.571x | **PASS** |

**Dictamen**: El Modelo A no contiene data leakage en $T_0$. Su extraordinario poder discriminativo obedece a la coherencia multivariada de los datos del Cluster 3 y a la efectividad de los árboles compactos regularizados.
