# Auditoría de Variables y Política de Control de Fuga de Datos (T0 / Data Leakage)
## Claro Colombia — Gerencia de Analítica Avanzada
**Proyecto:** Orquestación de Agentes de IA / Machine Learning (Cluster 3 Churn Mitigation)  
**Autor:** Neydher Antonio Martin Ramos  

---

## 1. Justificación Ejecutiva y Metodológica

En modelos de predicción de *Churn* y retención en telecomunicaciones, uno de los errores más comunes y costosos es el **Data Leakage (Fuga de Información Temporal)**. Ocurre cuando se introducen en el entrenamiento variables que no existían en el momento de la decisión ($T_0$) o que son el resultado de la propia acción que se pretende predecir o intervenir.

Para evitar sobreajustes engañosos (métricas artificialmente infladas en laboratorio que colapsan en producción), se auditó el 100% de las 129 variables de `Clientes_Cluster_3.xlsx` bajo una taxonomía formal de cinco roles.

---

## 2. Taxonomía de Roles de Variables (`feature_role`)

| Rol | Definición | Tratamiento en Baseline | Cantidad |
| :--- | :--- | :--- | :---: |
| **`PREDICTOR`** | Variables ex-ante legítimas de comportamiento, facturación histórica, calidad de red y consumo previas a $T_0$. | **INCLUIDAS** en el entrenamiento | **113** |
| **`TARGET_LEAKAGE`** | Variables que contienen información directa, proxy o simultánea del evento de intención o cancelación. | **EXCLUIDAS** estrictamente | **4** |
| **`POST_TREATMENT`** | Variables que reflejan intervenciones comerciales, reactivas o de soporte ejecutadas *después* de que se activó una alerta. | **EXCLUIDAS** estrictamente | **6** |
| **`TEMPORAL_UNCERTAIN`**| Variables cuya ventana temporal de captura respecto a $T_0$ no está certificada en el diccionario de datos. | **EXCLUIDAS** en baseline | **2** |
| **`IDENTIFIER`** | Metadatos de segmentación o periodo (`CLUSTER_ID`, `PERIODO`). | **EXCLUIDAS** de modelado | **2** |
| **`TARGET_MODEL_A`** | Variable objetivo de deserción efectiva (`BAN_CHURN`, prevalencia 0.52%). | **TARGET A** | **1** |
| **`TARGET_MODEL_B`** | Variable objetivo de alerta temprana (`BAN_INTENCION_CANCELACION`, 19.91%). | **TARGET B** | **1** |
| **Total** | | | **129** |

---

## 3. Matriz de Exclusión y Evidencia Literal

### 3.1 Variables Excluidas por Target Leakage
1. **`MOTIVO_LLAM_CANCELA`**
   * *Razón:* Marca binaria que indica si el cliente llamó a cancelar. Para el Modelo B (`BAN_INTENCION_CANCELACION`), es un sustituto directo del target. Para el Modelo A, contiene el resultado de la llamada de baja.
2. **`CANTIDAD_INTENCIONES`**
   * *Razón:* Contador anual de solicitudes de cancelación. Filtra el evento futuro si incluye el corte de análisis.
3. **`BAN_SOLICITUD_CAN` / `BAN_REINCIDENTE_30` / `BAN_REINCIDENTE_60`**
   * *Razón:* Marcas de solicitud de cancelación en ventanas de 30 y 60 días coincidentes con el target.

### 3.2 Variables Excluidas por Post-Treatment Leakage
1. **`BAN_OT_CERRADAS_DX` (o `BAN_OT_DX`)**
   * *Definición literal en diccionario:* *"Marca (1/0) que indica una orden de trabajo activa/cerrada de desconexión."*
   * *Categoría Claro:* *Intención de Cancelación & Churn*.
   * *Dictamen:* **DX = Desconexión.** La orden de trabajo técnica para desconectar el servicio se emite *después* de que el cliente solicita la baja. Incluirla falsea la causalidad del modelo.
2. **`BAN_RETENCION_ACTIVA`**
   * *Definición literal:* *"Marca (1/0) que indica si el cliente fue retenido con éxito en los últimos 12 meses."*
   * *Dictamen:* Refleja el éxito de un tratamiento de retención previo; correlaciona negativamente con churn (-0.203) debido a la política comercial, no al comportamiento natural.
3. **`BAN_CAMPANA_RETENCION` / `VAL_CAMPANA_RETENCION_36M` / `BAN_CAMPANA_CORRECTIVA` / `BAN_CAMPANA_ACTIVA`**
   * *Dictamen:* Codifican intervenciones comerciales correctivas aplicadas como respuesta al riesgo.

---

## 4. El "Silent Churn Gap" y la Justificación del Enfoque Dual

La auditoría cruzada reveló que de los **104 clientes que desertaron efectivamente (`BAN_CHURN = 1`)**:
* **52 clientes (50.0%)** presentaron `BAN_INTENCION_CANCELACION = 1`.
* **52 clientes (50.0%)** presentaron `BAN_INTENCION_CANCELACION = 0` (**Deserción Silenciosa**).

```text
               Total Bajas Efectivas (104)
                     ┌──────────┴──────────┐
                     ▼                     ▼
          Con Intención (52)     Sin Intención (52)
          "Ruta Observable"      "Silent Churn Gap"
                 │                         │
                 ▼                         ▼
         Modelo B (Intención)      Modelo A (Churn Directo)
```

**Conclusión Estratégica:**  
Un sistema que únicamente alerte sobre *intención de cancelación* deja desprotegido al 50% de los clientes que se dan de baja. El modelado predictivo dual (Modelo A para Churn silencioso + Modelo B para Intención) es la única arquitectura técnicamente completa para Claro Colombia.
