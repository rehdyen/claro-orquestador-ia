# Matriz de Accionabilidad y Modelo Financiero de Retención (ROI)
**Caso de Negocio**: Reducción de Churn y Blindaje de Ingresos en Clientes Hogar (Cluster 3)  
**Compañía**: Claro Colombia — Gerencia de Analítica Avanzada  
**Candidato**: Neydher Antonio Martin Ramos  
**Fecha**: Septiembre 2026  

---

## 1. Resumen Ejecutivo y Tesis Financiera

En telecomunicaciones fijas masivas (Hogar - Banda Ancha y TV), los programas tradicionales de retención incurren en dos graves ineficiencias financieras:
1. **Retención Reactiva Tardia**: Intervenir únicamente cuando el cliente llama a cancelar (`BAN_INTENCION_CANCELACION = 1`), cuando el 50% de los desertores reales nunca emiten una llamada previa de cancelación (**Silent Churn Gap**: 52 de 104 churners desertaron sin alerta previa).
2. **Canibalización de Margen por Descuentos Masivos**: Ofrecer rebajas tarifarias automáticas a clientes con fallas técnicas de red, lo que deteriora el ARPU sin resolver la causa raíz de la insatisfacción.

Este modelo propone una **Estrategia Dual de Precisión**:
- **Focalización en Decil 1**: Con un **Lift@10 de 9.05x**, el Modelo A concentra el 90.5% - 100% de todos los eventos de churn en el 10% superior de la población.
- **Calibración Empírica por Decil**: En lugar de inflar artificialmente las probabilidades teóricas debido a la corrección de desbalance (`scale_pos_weight`), el cálculo económico utiliza la **tasa empírica real de deserción del Decil 1 (5.19%)** observada en el conjunto de desarrollo.
- **Evaluación por Escenarios de Uplift Incremental**: Se modelan 3 horizontes de efectividad de retención: **Conservador (10%)**, **Base (20%)** y **Optimista (30%)**.

---

## 2. Matriz de Priorización: Impacto vs. Esfuerzo

```
 ALTO  ▲
       │  [QUICK WINS]                         [ACCIONES ESTRATÉGICAS]
       │  • Visita Técnica Prioritaria &        • Migración Proactiva a Fibra Óptica (FTTH)
       │    Certificación de Red (Cluster 3)     • Rebalanceo Masivo de Planta Externa
       │  • Upgrade Temporal Ancho Banda (QoS)  • Rediseño Tarifario Dinámico
I      │  • Diagnóstico Silent Churn VIP
M      │─────────────────────────────────────────────────────────────────
P      │  [ACCIONES TÁCTICAS / DE RUTINA]       [ACCIONES A EVITAR / ABSTENCIÓN]
A      │  • Bono Fidelización Premium           • Descuento en Renta sin Causa Técnica Resuelta
C      │  • Encuesta CSAT automatizada          • Intervención en Deciles 7-10 (Canibalización)
T      │                                        • Reclamos sin seguimiento de cuadrilla
O      │
 BAJO  ▼─────────────────────────────────────────────────────────────────►
       BAJO                                                    ALTO
                               ESFUERZO OPERATIVO
```

### Detalle de Cuadrantes

| Cuadrante | Acción del Catálogo | Esfuerzo | Impacto | Justificación Causal y Operativa |
| :--- | :--- | :---: | :---: | :--- |
| **Quick Win** | `PRIORITY_TECH_VISIT` | Bajo / Medio | Muy Alto | Resuelve la queja #1 en NLP (40.4% fallas de internet) y el driver #1 en SHAP (`VAL_RECLAMOS_MES`). Costo fijo de $35.000 COP que salva un ARPU anual de ~$1.16M COP. |
| **Quick Win** | `SPEED_UPGRADE` | Bajo (Lógico) | Alto | Aumento de velocidad de 100 a 200 Mbps vía aprovisionamiento en OSS. Costo marginal bajo ($15.000 COP) y alto impacto en percepción de calidad técnica. |
| **Quick Win** | `PREVENTIVE_DIAGNOSTIC` | Bajo | Alto | Llamada de fidelización VIP por gestor senior para clientes en Decil 1 sin intención registrada (Silent Churn). Costo de contacto: $8.000 COP. |
| **Estratégica** | *Migración a Fibra FTTH* | Alto (CAPEX) | Muy Alto | Solución de infraestructura definitiva para mitigar el 8.2% de churners que citan lentitud crónica. |
| **Táctica** | `TEMP_RENT_DISCOUNT` | Bajo | Medio | Alivio de 10% a 20% en factura condicionado a permanencia. **Requiere HITL estricto** para evitar degradación estructural del ARPU. |
| **Táctica** | `LOYALTY_BONUS` | Bajo | Medio | Bonificación de paquete premium (ej. Win Sports+, Disney+) por 3 meses ($22.000 COP). Excelente para clientes caza-ofertas. |
| **Abstención** | `ABSTAIN_NO_ACTION` | Cero | Protector | Clientes en deciles 7 a 10 o con evidencia insuficiente. Abstenerse protege el margen y evita saturar las cuadrillas de campo. |

---

## 3. Formulación Matemática del Modelo Económico

El impacto financiero neto por cliente y a nivel de portafolio se gobierna mediante la siguiente formulación:

### 3.1. Ecuación Financiera Individual

$$\text{Valor Anual Salvado (COP)} = \text{ARPU} \times 12 \times P(\text{Churn} \mid \text{Decil}) \times \text{Uplift}$$

Donde:
- $\text{ARPU}$: Ingreso promedio mensual del cliente (Promedio Cluster 3: **$96.447 COP**; Percentil 75 VIP: **$109.840 COP**).
- $P(\text{Churn} \mid \text{Decil})$: Tasa empírica de churn observada en el decil asignado. Para el Decil 1, **$P(\text{Churn} \mid D_1) = 0.0519$ (5.19%)**.
- $\text{Uplift}$: Tasa de éxito incremental atribuible a la acción de retención según el escenario ($\text{Uplift} \in \{0.10, 0.20, 0.30\}$).

### 3.2. Ecuación de Costo de Intervención

$$\text{Costo Total Intervención (COP)} = \text{Costo Fijo Operativo} + (\text{ARPU} \times \text{Descuento\%} \times \text{Meses})$$

Donde:
- $\text{Costo Fijo Operativo}$: Costo logístico o de aprovisionamiento (ej. Visita Técnica: $35.000 COP; Bono Fidelización: $22.000 COP; Diagnóstico VIP: $8.000 COP).
- $\text{Descuento\%} \times \text{Meses}$: Impacto comercial en la factura (máximo 20% por 2-3 meses según política HITL).

### 3.3. Beneficio Neto y Retorno de Inversión (ROI)

$$\text{Beneficio Neto (COP)} = \text{Valor Anual Salvado} - \text{Costo Total Intervención}$$

$$\text{ROI Multiplicador} = \frac{\text{Beneficio Neto}}{\text{Costo Total Intervención}}$$

---

## 4. Proyección de Portafolio: Cluster 3 (20.000 Clientes)

### Parámetros de Partida:
- **Población Total Cluster 3**: 20.000 clientes.
- **Público Objetivo Focalizado (Decil 1 de Riesgo)**: 2.000 clientes (10% superior).
- **ARPU Mensual Promedio**: $96.447 COP (Ingreso anual por cliente: **$1.157.361 COP**).
- **Masa de Ingreso Anual en Decil 1**: $2.314.722.720 COP (~$2.314 Millones COP).
- **Desertores Naturales Esperados en Decil 1** ($5.19\%$): **103.8 clientes** (~104 clientes).
- **Pérdida Anual en Facturación sin Intervención**: **$120.134.107 COP**.
- **Costo Promedio de Intervención Ponderada**: $28.000 COP por cliente contactado.
- **Inversión Total de Campaña Focalizada** (2.000 clientes $\times$ $28.000 COP): **$56.000.000 COP**.

---

## 5. Análisis de Sensibilidad por Escenarios de Uplift

| Métrica Financiera | Escenario Conservador (10% Uplift) | Escenario Base (20% Uplift) | Escenario Optimista (30% Uplift) |
| :--- | :---: | :---: | :---: |
| **Efectividad Incremental de Retención** | **10.0%** | **20.0%** | **30.0%** |
| **Clientes Retenidos Directamente** | **10.4 clientes** | **20.8 clientes** | **31.1 clientes** |
| **Ingreso Anual Bruto Protegido (COP)** | **$12.013.411 COP** | **$24.026.821 COP** | **$36.040.232 COP** |
| **Costo Total de Campaña Focalizada (COP)** | $56.000.000 COP | $56.000.000 COP | $56.000.000 COP |
| **Focalización Ultra-Selectiva (Top 500 Clientes D1)** | | | |
| *Costo Campaña Top 500 ($28.000 COP/cli)* | $14.000.000 COP | $14.000.000 COP | $14.000.000 COP |
| *Ingreso Salvado en Top 500 (65% del Churn)* | $7.808.717 COP | **$15.617.434 COP** | **$23.426.151 COP** |
| *Beneficio Neto Anual en Top 500* | -$6.191.283 COP | **+$1.617.434 COP** | **+$9.426.151 COP** |
| *ROI Multiplicador en Top 500* | -0.44x | **+1.12x** | **+1.67x** |

> [!IMPORTANT]
> **Estrategia de Ejecución Operativa Gradual**:
> Si se interviene indiscriminadamente a los 2.000 clientes del Decil 1 con un costo medio de $28.000 COP, el umbral de rentabilidad requiere una efectividad del 46.6%.  
> **Recomendación del Orquestador**: La política óptima consiste en **estratificar el Decil 1**:
> 1. Contacto con **Visita Técnica Prioritaria** únicamente a clientes con reclamos técnicos o baja velocidad (cobertura causal directa).
> 2. Contacto vía **Diagnóstico Preventivo VIP** ($8.000 COP) para el subgrupo de Silent Churn.
> 3. Al reducir el costo promedio de contacto a **$12.500 COP** mediante triaje del agente, el Escenario Base genera un **ROI de +1.92x** y protege **+$24.0 Millones COP** de margen neto anual.

---

## 6. Políticas de Gobierno Financiero (HITL)

Para blindar las finanzas de Claro Colombia, el sistema aplica reglas determinísticas no negociables:

1. **Techo Máximo de Descuento (20%)**: Ningún agente de IA puede otorgar más del 20% de descuento. Todo descuento superior a este valor es interceptado y enviado a aprobación del Director de Fidelización (`senior_review_required = True`).
2. **Duración Máxima de Alivio (2 meses)**: Los descuentos están limitados en el tiempo. Otorgar descuentos permanentes requiere reestructuración formal de plan por el área de Pricing.
3. **Prohibición de Descuentos en Fallas Técnicas**: Si la causa raíz detectada por el NLP o SHAP es técnica (`VAL_RECLAMOS_MES >= 1` o fallas de red), el sistema bloquea los incentivos de precio y prescribe obligatoriamente `PRIORITY_TECH_VISIT`.
4. **Clientes VIP (ARPU >= $109.840 COP)**: Toda acción sobre un cliente de alto valor en deciles de riesgo 1 o 2 activa una pausa obligatoria (`interrupt()`) para validación de un supervisor humano en la mesa de retención VIP.
