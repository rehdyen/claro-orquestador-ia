# Matriz de Accionabilidad y Modelo Financiero de Retención (ROI)
**Caso de Negocio**: Reducción de Churn y Blindaje de Ingresos en Clientes Hogar (Cluster 3)  
**Compañía**: Claro Colombia — Gerencia de Analítica Avanzada  
**Candidato**: Neydher Antonio Martin Ramos  
**Fecha**: Septiembre 2026  

---

## 1. Resumen Ejecutivo y Tesis Financiera

En telecomunicaciones fijas masivas (Hogar - Banda Ancha y TV), los programas tradicionales de retención incurren en dos graves ineficiencias financieras:
1. **Retención Reactiva Tardía**: Intervenir únicamente cuando el cliente llama a cancelar (`BAN_INTENCION_CANCELACION = 1`), cuando el 50% de los desertores reales nunca emiten una llamada previa de cancelación (**Silent Churn Gap**: 52 de 104 churners desertaron sin alerta previa).
2. **Canibalización de Margen por Descuentos Masivos**: Ofrecer rebajas tarifarias automáticas a clientes con fallas técnicas de red, lo que deteriora el ARPU sin resolver el problema de calidad de servicio.

Este modelo propone una **Estrategia Dual de Precisión**:
- **Focalización en Decil 1**: Con un **Lift@10 de 9.05x**, el Modelo A concentra el 90.5% - 100% de todos los eventos de churn en el 10% superior de la población.
- **Calibración Empírica por Decil**: En lugar de inflar artificialmente las probabilidades teóricas debido a la corrección de desbalance (`scale_pos_weight`), el cálculo económico utiliza la **tasa empírica real de deserción del Decil 1 (5.19%)** observada en el conjunto de desarrollo.
- **Evaluación por Escenarios de Uplift Incremental**: Se modelan 3 horizontes de efectividad incremental de retención: **Conservador (10%)**, **Base (20%)** y **Optimista (30%)**, etiquetados siempre como supuestos analíticos para evaluación de sensibilidad.

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
A      │  • Bono Fidelización Premium           • Descuento en Renta sin Falla Técnica Resuelta
C      │  • Encuesta CSAT automatizada          • Intervención en Deciles 7-10 (Canibalización)
T      │                                        • Reclamos sin seguimiento de cuadrilla
O      │
 BAJO  ▼─────────────────────────────────────────────────────────────────►
       BAJO                                                    ALTO
                               ESFUERZO OPERATIVO
```

### Detalle de Cuadrantes

| Cuadrante | Acción del Catálogo | Esfuerzo | Impacto | Justificación Operativa y Evidencia |
| :--- | :--- | :---: | :---: | :--- |
| **Quick Win** | `PRIORITY_TECH_VISIT` | Bajo / Medio | Muy Alto | Responde a la queja técnica en NLP (24.6% fallas de internet) y al driver #1 en SHAP (`VAL_RECLAMOS_MES`). Costo fijo de $35.000 COP que busca proteger un ARPU anual de ~$1.16M COP. |
| **Quick Win** | `SPEED_UPGRADE` | Bajo (Lógico) | Alto | Aumento de velocidad en clientes con planes $\le 50$ Mbps sin reclamos físicos. Aprovisionamiento lógico en OSS a costo marginal ($15.000 COP). |
| **Quick Win** | `PREVENTIVE_DIAGNOSTIC` | Bajo | Alto | Llamada de fidelización VIP por gestor senior para clientes en Decil 1 sin intención registrada (Silent Churn). Costo de contacto: $8.000 COP. |
| **Estratégica** | *Migración a Fibra FTTH* | Alto (CAPEX) | Muy Alto | Solución de infraestructura definitiva para mitigar la lentitud crónica reportada en la voz del cliente. |
| **Táctica** | `TEMP_RENT_DISCOUNT` | Bajo | Medio | Alivio de 10% a 20% en factura condicionado a permanencia. **Máximo estándar de 2 meses**; extensiones a 3 meses requieren **Senior Review obligatoria**. |
| **Táctica** | `LOYALTY_BONUS` | Bajo | Medio | Bonificación de paquete premium (ej. Win Sports+, Disney+) por 3 meses ($22.000 COP) para clientes con patrones de caza-ofertas. |
| **Abstención** | `ABSTAIN_NO_ACTION` | Cero | Protector | Clientes en deciles 7 a 10 o con evidencia insuficiente. Abstenerse protege el margen y evita saturar las cuadrillas de campo. |

---

## 3. Formulación Matemática del Modelo Económico

El impacto financiero neto por cliente y a nivel de portafolio se gobierna mediante la siguiente formulación estándar:

### 3.1. Ecuaciones Financieras

$$\text{ExpectedAvoidedChurn} = N_{\text{target}} \times \text{empirical\_churn\_rate} \times \text{intervention\_uplift}$$

$$\text{ProtectedRevenue} = \text{ExpectedAvoidedChurn} \times \text{ARPU\_monthly} \times \text{horizon\_months}$$

$$\text{InterventionCost} = \text{fixed\_cost} + \text{variable\_action\_costs} + \text{discount\_costs}$$

$$\text{BenefitCostRatio (B/C)} = \frac{\text{ProtectedRevenue}}{\text{InterventionCost}}$$

$$\text{NetROI} = \frac{\text{ProtectedRevenue} - \text{InterventionCost}}{\text{InterventionCost}} = \text{BenefitCostRatio} - 1$$

---

## 4. Proyección de Portafolio: Cluster 3 (20.000 Clientes)

### Parámetros de Partida:
- **Población Total Cluster 3**: 20.000 clientes.
- **Público Objetivo Focalizado (Decil 1 de Riesgo)**: 2.000 clientes (10% superior).
- **ARPU Mensual Promedio**: $96.447 COP (Ingreso anual por cliente: **$1.157.361 COP**).
- **Masa de Ingreso Anual en Decil 1**: $2.314.722.720 COP (~$2.314 Millones COP).
- **Tasa Empírica de Churn en Decil 1**: **5.19%** (83 churners en 1.600 casos dev).
- **Desertores Naturales Esperados en Decil 1**: **103.8 clientes** (~104 clientes).
- **Pérdida Anual en Facturación sin Intervención**: **$120.134.109 COP**.

---

## 5. Comparativa de Estrategias: Campaña Masiva vs. Triaje Selectivo

### Estrategia A: Intervención Masiva a todo el Decil 1 (2.000 Clientes a $28.000 COP promedio)
*Inversión Total de Campaña: $56.000.000 COP.*

| Escenario | Uplift | Evitados | Protected Revenue | Campaign Cost | Benefit/Cost | Net ROI (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Conservador** | 10.0% | 10.4 | $12.013.411 COP | $56.000.000 COP | 0.21x | -78.5% |
| **Base** | 20.0% | 20.8 | $24.026.822 COP | $56.000.000 COP | 0.43x | -57.1% |
| **Optimista** | 30.0% | 31.1 | $36.040.233 COP | $56.000.000 COP | 0.64x | -35.6% |

> [!WARNING]
> **Lección Financiera Clave**: Intervenir indiscriminadamente a los 2.000 clientes de Decil 1 con un costo promedio de $28.000 COP destruye valor porque la tasa natural de churn es del 5.19%.  
> El valor del sistema multi-agente no reside en enviar cuadrillas masivas, sino en **aplicar triaje de alta eficiencia**.

---

### Estrategia B: Triaje Selectivo Top 500 (Enfoque Oficial de Negocio)
*Se prioriza a los 500 clientes con mayor severidad en el Decil 1 (concentran ~65% de los churners = 67.5 casos).*  
*El orquestador asigna acciones según evidencia: Diagnóstico VIP ($8k) para Silent Churn, Visita ($35k) sólo ante reclamo activo, Upgrade ($15k) para baja velocidad.*  
*Costo promedio de contacto ponderado: **$12.500 COP** $\rightarrow$ **Inversión Total: $6.250.000 COP**.*

| Escenario | Uplift | Clientes Salvados | Protected Revenue | Campaign Cost | Beneficio Neto | Benefit/Cost | Net ROI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Conservador** | 10.0% | 6.8 | $7.812.189 COP | $6.250.000 COP | +$1.562.189 COP | **1.25x** | **+25.0%** |
| **Base** | 20.0% | 13.5 | $15.624.378 COP | $6.250.000 COP | **+$9.374.378 COP** | **2.50x** | **+1.50x (+150%)** |
| **Optimista** | 30.0% | 20.2 | $23.436.568 COP | $6.250.000 COP | +$17.186.568 COP | **3.75x** | **+2.75x (+275%)** |

> [!IMPORTANT]
> En el **Escenario Base**, el triaje selectivo genera:
> - **Ingreso Bruto Protegido**: **$15.62M COP**
> - **Inversión de Campaña**: **$6.25M COP**
> - **Beneficio Económico Neto**: **+$9.37M COP**
> - **Benefit-Cost Ratio**: **2.50x** (se recuperan $2.50 COP por cada peso invertido)
> - **Net ROI**: **+1.50x (+150.0%)**

---

## 6. Políticas de Gobierno Financiero (HITL)

1. **Techo Máximo de Descuento (20%)**: Ningún agente de IA puede otorgar más del 20% de descuento. Todo descuento superior activa escalamiento inmediato (`senior_review_required = True`).
2. **Duración Máxima Autorizada (2 meses)**: Los descuentos están limitados a 2 meses. Cualquier propuesta de 3 meses se escala obligatoriamente a Senior Review.
3. **Falla Técnica $\neq$ Rebaja Comercial**: Si la evidencia dominante es técnica (`VAL_RECLAMOS_MES >= 1` o degradación de red), el sistema bloquea los descuentos tarifarios y prescribe `PRIORITY_TECH_VISIT` o `SPEED_UPGRADE`.
4. **Clientes VIP (ARPU >= $109.840 COP)**: Toda acción sobre un cliente de alto valor en deciles de riesgo 1 o 2 activa una pausa obligatoria (`interrupt()`) para validación de un supervisor humano.
