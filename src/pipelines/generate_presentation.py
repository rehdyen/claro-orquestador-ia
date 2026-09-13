"""
src/pipelines/generate_presentation.py
======================================
Generador automatizado del Deck Ejecutivo de Sustentación (11 Diapositivas 16:9):
- Orquestador de Agentes de IA / Machine Learning (Claro Colombia)
- Candidato: Neydher Antonio Martin Ramos
- Evaluador: Rafael José Del Castillo Pavajeau
"""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Colores Corporativos
CLARO_RED = RGBColor(218, 41, 28)       # #DA291C
DARK_NAVY = RGBColor(15, 23, 42)        # #0F172A
SLATE_GRAY = RGBColor(71, 85, 105)      # #475569
LIGHT_BG = RGBColor(248, 250, 252)      # #F8FAFC
CARD_BG = RGBColor(255, 255, 255)       # #FFFFFF
BORDER_COLOR = RGBColor(226, 232, 240)  # #E2E8F0
GREEN_TEXT = RGBColor(16, 185, 129)     # #10B981
AMBER_TEXT = RGBColor(217, 119, 6)      # #D97706
BLUE_ACCENT = RGBColor(37, 99, 235)     # #2563EB


def create_base_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def add_header(slide, title: str, subtitle: str, slide_num: int):
    # Fondo general
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = LIGHT_BG
    bg.line.fill.background()

    # Barra de acento Claro en el tope
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.12))
    bar.fill.solid()
    bar.fill.fore_color.rgb = CLARO_RED
    bar.line.fill.background()

    # Título y Subtítulo
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.5), Inches(1.1))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_sub = tf.paragraphs[0]
    p_sub.text = subtitle.upper()
    p_sub.font.size = Pt(10)
    p_sub.font.bold = True
    p_sub.font.color.rgb = CLARO_RED
    p_sub.space_after = Pt(2)

    p_title = tf.add_paragraph()
    p_title.text = title
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = DARK_NAVY

    # Footer
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.4))
    ftf = footer_box.text_frame
    p_foot = ftf.paragraphs[0]
    p_foot.text = f"Claro Colombia | Gerencia de Analítica Avanzada — Sustentación Orquestador de Agentes IA | Slide {slide_num}/11"
    p_foot.font.size = Pt(9)
    p_foot.font.color.rgb = SLATE_GRAY


def add_card(slide, left, top, width, height, fill_color=CARD_BG, border_color=BORDER_COLOR):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    return card


# ==============================================================================
# 1. PORTADA
# ==============================================================================
def build_slide_1(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Fondo oscuro
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK_NAVY
    bg.line.fill.background()

    # Acento superior Claro
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.2))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = CLARO_RED
    top_bar.line.fill.background()

    # Contenedor central
    box = slide.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(4.0))
    tf = box.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "PROCESO DE SELECCIÓN — GERENCIA DE ANALÍTICA AVANZADA"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = CLARO_RED
    p0.space_after = Pt(12)

    p1 = tf.add_paragraph()
    p1.text = "Sistema Multi-Agente y Modelado Dual para Retención de Clientes Hogar"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)
    p1.space_after = Pt(14)

    p2 = tf.add_paragraph()
    p2.text = "Detección Temprana, Explicabilidad Causal (NLP + SHAP) y Orquestación Autónoma con Supervisión Humana (HITL)"
    p2.font.size = Pt(16)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_after = Pt(36)

    p3 = tf.add_paragraph()
    p3.text = "Candidato: Neydher Antonio Martin Ramos  |  Evaluador: Rafael José Del Castillo Pavajeau\nRol: Orquestador de Agentes de IA / Machine Learning  |  Fecha: Septiembre 2026"
    p3.font.size = Pt(12)
    p3.font.color.rgb = RGBColor(148, 163, 184)


# ==============================================================================
# 2. EL DIAGNÓSTICO Y EL SILENT CHURN GAP
# ==============================================================================
def build_slide_2(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "El Diagnóstico y el Hallazgo Oculto: 'Silent Churn Gap'", "Punto de Partida del Negocio", 2)

    # Card 1: Contexto Cluster 3
    add_card(slide, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
    tb1 = slide.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "Radiografía del Cluster 3 (20.000 Abonados Hogar)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY
    p.space_after = Pt(14)

    bullets1 = [
        ("Alta Concentración de Valor: ", "ARPU medio de $96.447 COP y percentil 75 en $109.840 COP. Masa de facturación anual de ~$23.140 Millones COP."),
        ("Baja Prevalencia Global de Churn: ", "Solo el 0.52% (104 clientes) cancelaron formalmente. Sin embargo, el 19.91% (3.981 clientes) registraron intención de retiro."),
        ("Falsa Equivalencia Tradicional: ", "En la industria suele asumirse que quien tiene intención es quien deserta. Los datos demuestran lo contrario: son poblaciones con dinámicas distintas.")
    ]
    for b_title, b_desc in bullets1:
        p_b = tf1.add_paragraph()
        p_b.font.size = Pt(12)
        p_b.space_after = Pt(10)
        run1 = p_b.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = b_desc
        run2.font.color.rgb = SLATE_GRAY

    # Card 2: El Descubrimiento Crítico
    add_card(slide, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    tb2 = slide.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p2 = tf2.paragraphs[0]
    p2.text = "El 'Silent Churn Gap': 52 / 52 (Fuga No Detectada)"
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = CLARO_RED
    p2.space_after = Pt(14)

    bullets2 = [
        ("50% de Churners Sin Intención Previa: ", "Exactamente 52 de los 104 desertores NUNCA llamaron a radicar intención de cancelación. Se marcharon en silencio."),
        ("El Punto Ciego de la Operación: ", "Si Claro solo interviene la cola de llamadas de cancelación (Call Center de Retención), el 50% de la fuga es 100% invisible para el negocio."),
        ("Implicación Estratégica Ineludible: ", "Se requieren DOS MODELOS ESPECIALIZADOS: uno para capturar la deserción silenciosa (Modelo A) y otro para contener la intención explícita (Modelo B).")
    ]
    for b_title, b_desc in bullets2:
        p_b = tf2.add_paragraph()
        p_b.font.size = Pt(12)
        p_b.space_after = Pt(10)
        run1 = p_b.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = b_desc
        run2.font.color.rgb = SLATE_GRAY


# ==============================================================================
# 3. VOZ DEL CLIENTE (NLP)
# ==============================================================================
def build_slide_3(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "Voz del Cliente (VoC): Evidencia Estructurada de 500 Llamadas", "Inteligencia Semántica No Estructurada", 3)

    # Card Izquierda: Texto
    add_card(slide, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
    tb = slide.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Taxonomía Congelada & Procesamiento Robusto"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY
    p.space_after = Pt(12)

    bullets = [
        ("Procesamiento Masivo y Blindado: ", "500 llamadas analizadas con 0 errores Pydantic. Taxonomía cerrada de 6 macro-motivos y 24 sub-motivos con spans de evidencia exacta."),
        ("Dominancia de Falla Técnica: ", "El 40.4% de las quejas corresponden a problemas de internet, lentitud y microcortes de red."),
        ("Contraste Radical vs Otros Clusters: ", "Cluster 3 exhibe 2.3 veces más reclamos técnicos que los clusters 1 y 2, y un 35% más menciones de demora en visitas."),
        ("Causalidad Descubierta: ", "Los clientes no desertan por falta de ofertas comerciales; desertan porque el internet falla y la visita técnica se demora.")
    ]
    for b_title, b_desc in bullets:
        p_b = tf.add_paragraph()
        p_b.font.size = Pt(11)
        p_b.space_after = Pt(8)
        run1 = p_b.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = b_desc
        run2.font.color.rgb = SLATE_GRAY

    # Card Derecha: Imagen Gráfica NLP
    add_card(slide, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    img_path = "outputs/figures/nlp_cluster3_contrast.png"
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(7.0), Inches(1.8), width=Inches(5.3))


# ==============================================================================
# 4. ARQUITECTURA PREDICTIVA DUAL
# ==============================================================================
def build_slide_4(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "Arquitectura Predictiva Dual: Separando Fuga de Intención", "Diseño de Machine Learning Orientado al Problema", 4)

    # Card Modelo A
    add_card(slide, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
    tb1 = slide.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p1 = tf1.paragraphs[0]
    p1.text = "MODELO A: Churn Efectivo Real (BAN_CHURN)"
    p1.font.size = Pt(15)
    p1.font.bold = True
    p1.font.color.rgb = CLARO_RED
    p1.space_after = Pt(12)

    bullets1 = [
        ("Naturaleza del Target: ", "Evento terminal real (Desconexión definitiva del servicio en facturación). Prevalencia: 0.52% (Aguja en un pajar)."),
        ("Estrategia Algorítmica: ", "LightGBM con árboles deliberadamente compactos (max_depth=3, num_leaves=7) y scale_pos_weight dinámico para no memorizar ruido."),
        ("Validación Blindada: ", "RepeatedStratifiedKFold (4 splits x 5 repeats = 20 evaluaciones independientes) + Holdout ciego."),
        ("Misión Operativa: ", "Detectar la deserción silenciosa y alimentar campañas preventivas en planta externa y fidelización técnica.")
    ]
    for b_title, b_desc in bullets1:
        p_b = tf1.add_paragraph()
        p_b.font.size = Pt(11)
        p_b.space_after = Pt(8)
        run1 = p_b.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = b_desc
        run2.font.color.rgb = SLATE_GRAY

    # Card Modelo B
    add_card(slide, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    tb2 = slide.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p2 = tf2.paragraphs[0]
    p2.text = "MODELO B: Intención de Cancelación"
    p2.font.size = Pt(15)
    p2.font.bold = True
    p2.font.color.rgb = BLUE_ACCENT
    p2.space_after = Pt(12)

    bullets2 = [
        ("Naturaleza del Target: ", "Intención manifiesta radicada por el cliente (`BAN_INTENCION_CANCELACION`). Prevalencia: 19.91% (Alta densidad)."),
        ("Estrategia Algorítmica: ", "LightGBM con mayor capacidad de partición (max_depth=4, num_leaves=15, learning_rate=0.03)."),
        ("Validación Metodológica: ", "StratifiedKFold (5 splits balanceados) + Holdout ciego de 4.000 clientes."),
        ("Misión Operativa: ", "Priorizar llamadas entrantes en Call Center y facultar a los asesores de primera línea con ofertas comerciales retenedoras.")
    ]
    for b_title, b_desc in bullets2:
        p_b = tf2.add_paragraph()
        p_b.font.size = Pt(11)
        p_b.space_after = Pt(8)
        run1 = p_b.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = b_desc
        run2.font.color.rgb = SLATE_GRAY


# ==============================================================================
# 5. RIGOR METODOLÓGICO Y HONESTIDAD ESTADÍSTICA
# ==============================================================================
def build_slide_5(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "Rigor Metodológico: Cero Fuga T0 y Lift@10 = 9.05x", "Honestidad Estadística y Métricas Holdout", 5)

    # Card Izquierda: Métricas y Leakage
    add_card(slide, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
    tb = slide.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Auditoría de Fuga T0 & Métricas con Bootstrap"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY
    p.space_after = Pt(10)

    bullets = [
        ("Descarte Riguroso de Fugas T0: ", "Se identificaron y eliminaron variables espurias como `ESTADO_FUENTE_C` (proxy de liquidación), `VAL_SALDO_ACTUAL` (saldo en 0) y `BAN_OT_CERRADAS_DX` (orden de desconexión). Cero datos futuros."),
        ("Modelo A (Churn 0.52%): ", "Lift@10 en Holdout: 9.048x (IC 95%: [7.619 - 10.000x]). En el top 10% de clientes contactados se captura el 90.5% del churn total. ROC-AUC: 0.9569, PR-AUC: 0.4738."),
        ("Modelo B (Intención 19.9%): ", "Lift@10 en Holdout: 3.812x (IC 95%: [3.603 - 4.034x]). PR-AUC: 0.6278, ROC-AUC: 0.8248.")
    ]
    for b_title, b_desc in bullets:
        p_b = tf.add_paragraph()
        p_b.font.size = Pt(11)
        p_b.space_after = Pt(8)
        run1 = p_b.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = b_desc
        run2.font.color.rgb = SLATE_GRAY

    # Card Derecha: Curvas de Lift y PR
    add_card(slide, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    img_path = "outputs/figures/lift_and_pr_curves.png"
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(6.9), Inches(1.8), width=Inches(5.5))


# ==============================================================================
# 6. EXPLICABILIDAD Y CAUSALIDAD (SHAP + NLP)
# ==============================================================================
def build_slide_6(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "Explicabilidad y Causalidad: Convergencia de SHAP y NLP", "De la Correlación a la Causa Raíz", 6)

    # Card Izquierda: Texto Causal
    add_card(slide, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
    tb = slide.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Convergencia Temática Multimodal"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DARK_NAVY
    p.space_after = Pt(10)

    bullets = [
        ("Driver #1: VAL_RECLAMOS_MES: ", "Cada reclamo mensual dispara exponencialmente el log-odds de deserción en SHAP. Coincide con las quejas de lentitud en NLP."),
        ("Driver #2: VELOCIDAD_INTERNET_MBPS: ", "Clientes con planes <= 50 Mbps sufren una fricción técnica constante, amplificada por el consumo de streaming de los hogares."),
        ("Driver #3: VAL_VAR_RENTA & RENTA_ACTUAL: ", "Incrementos tarifarios no explicados en la factura disparan la fuga de clientes con más de 12 meses de antigüedad."),
        ("Conclusión de Causalidad: ", "El cliente se va por FALLA TÉCNICA persistente. Una rebaja comercial sin solución de red solo retrasa el churn 30 días.")
    ]
    for b_title, b_desc in bullets:
        p_b = tf.add_paragraph()
        p_b.font.size = Pt(11)
        p_b.space_after = Pt(8)
        run1 = p_b.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = b_desc
        run2.font.color.rgb = SLATE_GRAY

    # Card Derecha: Beeswarm SHAP
    add_card(slide, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    img_path = "outputs/figures/shap_beeswarm_model_a.png"
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(7.0), Inches(1.8), width=Inches(5.3))


# ==============================================================================
# 7. SISTEMA MULTI-AGENTE (LANGGRAPH + HITL)
# ==============================================================================
def build_slide_7(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "El Sistema Multi-Agente: Orquestación LangGraph con HITL", "Arquitectura Autónoma con Supervisión Humana", 7)

    # 3 Cards Horizontales
    card_w = Inches(3.7)
    card_h = Inches(5.0)

    # Agentes Analíticos
    add_card(slide, Inches(0.8), Inches(1.6), card_w, card_h)
    tb1 = slide.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(3.3), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "1. Agentes Especialistas\n(Paralelismo Seguro)"
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = DARK_NAVY
    p1.space_after = Pt(10)
    p1_desc = tf1.add_paragraph()
    p1_desc.text = "• Customer Intelligence Agent: Ejecuta inferencia dual en milisegundos, asigna deciles y detecta el Silent Churn Pattern.\n\n• VoC / NLP Agent: Desacoplado; consulta perfiles de quejas y extrae evidencias semánticas sin cruzar datos ilegalmente.\n\n• Estado Reducible: LangGraph combina sus hallazgos en paralelo mediante reducers thread-safe."
    p1_desc.font.size = Pt(11)
    p1_desc.font.color.rgb = SLATE_GRAY

    # Orquestador y Juez
    add_card(slide, Inches(4.8), Inches(1.6), card_w, card_h)
    tb2 = slide.shapes.add_textbox(Inches(5.0), Inches(1.8), Inches(3.3), Inches(4.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p2 = tf2.paragraphs[0]
    p2.text = "2. Orquestador & Juez\n(Causalidad y Políticas)"
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = DARK_NAVY
    p2.space_after = Pt(10)
    p2_desc = tf2.add_paragraph()
    p2_desc.text = "• Retention Orchestrator: Cruza causa raíz con el catálogo oficial y computa el ROI con tasa empírica por decil.\n\n• Deterministic Judge Agent: Aplica reglas inviolables de negocio. Si el orquestador propone una acción incompatible o fuera de catálogo, rechaza y fuerza una re-planificación con reintento acotado (1 loop)."
    p2_desc.font.size = Pt(11)
    p2_desc.font.color.rgb = SLATE_GRAY

    # Human-in-the-Loop
    add_card(slide, Inches(8.8), Inches(1.6), card_w, card_h)
    tb3 = slide.shapes.add_textbox(Inches(9.0), Inches(1.8), Inches(3.3), Inches(4.5))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p3 = tf3.paragraphs[0]
    p3.text = "3. Human-in-the-Loop\n(Pausa Activa 'interrupt()')"
    p3.font.size = Pt(14)
    p3.font.bold = True
    p3.font.color.rgb = CLARO_RED
    p3.space_after = Pt(10)
    p3_desc = tf3.add_paragraph()
    p3_desc.text = "• Checkpoint Nativo: La ejecución se suspende automáticamente si se toca dinero, si el descuento excede el 20%, si es cliente VIP o Silent Churn.\n\n• Control Humano: El supervisor de Claro aprueba, ajusta o rechaza en su bandeja.\n\n• Resunción Transparente: El grafo se reanuda con el veredicto humano inmutable."
    p3_desc.font.size = Pt(11)
    p3_desc.font.color.rgb = SLATE_GRAY


# ==============================================================================
# 8. GOBERNANZA Y CATÁLOGO DE ACCIONES
# ==============================================================================
def build_slide_8(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "Gobernanza y Catálogo de Acciones: Coherencia Causal", "Blindaje Operativo y Protocolo FastMCP", 8)

    # Card Izquierda: Reglas de Gobernanza
    add_card(slide, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
    tb1 = slide.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p1 = tf1.paragraphs[0]
    p1.text = "Reglas de Gobierno No Negociables"
    p1.font.size = Pt(15)
    p1.font.bold = True
    p1.font.color.rgb = DARK_NAVY
    p1.space_after = Pt(10)

    bullets1 = [
        ("Falla Técnica != Descuento Comercial: ", "Queda estrictamente prohibido otorgar rebajas de renta si el cliente tiene reclamos de internet sin visita técnica asignada."),
        ("Techo Máximo de Descuento: ", "Ningún agente puede autorizar más del 20% de descuento. Casos superiores activan `senior_review_required = True`."),
        ("Duración Acotada: ", "Máximo 2 meses de descuento temporal condicionado a permanencia. Previene erosión permanente de ARPU."),
        ("FastMCP como Protocolo Seguro: ", "Herramientas expuestas bajo el estándar Model Context Protocol con esquemas fuertemente tipados.")
    ]
    for b_title, b_desc in bullets1:
        p_b = tf1.add_paragraph()
        p_b.font.size = Pt(11)
        p_b.space_after = Pt(8)
        run1 = p_b.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = b_desc
        run2.font.color.rgb = SLATE_GRAY

    # Card Derecha: El Catálogo Oficial
    add_card(slide, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    tb2 = slide.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p2 = tf2.paragraphs[0]
    p2.text = "Catálogo Oficial de Acciones Claro"
    p2.font.size = Pt(15)
    p2.font.bold = True
    p2.font.color.rgb = DARK_NAVY
    p2.space_after = Pt(10)

    actions = [
        ("PRIORITY_TECH_VISIT ($35.000 COP): ", "Visita técnica prioritaria en menos de 24h para certificación de acometida y módem."),
        ("SPEED_UPGRADE ($15.000 COP): ", "Aumento de velocidad (ej. 100 a 200 Mbps) por aprovisionamiento lógico FTTH."),
        ("TEMP_RENT_DISCOUNT (10-20%): ", "Descuento temporal de 2 meses para clientes con shock tarifario o antigüedad > 12 meses."),
        ("PREVENTIVE_DIAGNOSTIC ($8.000 COP): ", "Llamada de fidelización VIP por gestor senior para capturar el Silent Churn."),
        ("ABSTAIN_NO_ACTION ($0 COP): ", "Abstención estratégica en deciles sanos (7-10) para proteger el margen comercial.")
    ]
    for a_title, a_desc in actions:
        p_b = tf2.add_paragraph()
        p_b.font.size = Pt(11)
        p_b.space_after = Pt(8)
        run1 = p_b.add_run()
        run1.text = a_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = a_desc
        run2.font.color.rgb = SLATE_GRAY


# ==============================================================================
# 9. IMPACTO FINANCIERO Y ROI
# ==============================================================================
def build_slide_9(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "Impacto Financiero y ROI: Escenarios de Uplift Incremental", "Justificación Económica Basada en Deciles Empíricos", 9)

    # Card 1: Fundamento Matemático
    add_card(slide, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
    tb1 = slide.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p1 = tf1.paragraphs[0]
    p1.text = "Ecuación Financiera de Retención"
    p1.font.size = Pt(15)
    p1.font.bold = True
    p1.font.color.rgb = DARK_NAVY
    p1.space_after = Pt(10)

    bullets1 = [
        ("Base Empírica de Riesgo: ", "No se utiliza la probabilidad bruta inflada por ponderación de clases, sino la tasa empírica observada en Decil 1: 5.19%."),
        ("Valor Anual Salvado: ", "ARPU ($96.447) * 12 meses * P(Churn|Decil 1) * Uplift Incremental."),
        ("Costo de Intervención: ", "Costo Operativo Directo + (ARPU * Descuento % * Meses de Descuento)."),
        ("Masa Expuesta Decil 1 (2.000 clientes): ", "$2.314 Millones COP anuales. Con 104 churners naturales esperados (~$120.1 Millones COP en riesgo anual).")
    ]
    for b_title, b_desc in bullets1:
        p_b = tf1.add_paragraph()
        p_b.font.size = Pt(11)
        p_b.space_after = Pt(8)
        run1 = p_b.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = b_desc
        run2.font.color.rgb = SLATE_GRAY

    # Card 2: Escenarios de Uplift
    add_card(slide, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    tb2 = slide.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p2 = tf2.paragraphs[0]
    p2.text = "Sensibilidad por Escenarios (Uplift Incremental)"
    p2.font.size = Pt(15)
    p2.font.bold = True
    p2.font.color.rgb = GREEN_TEXT
    p2.space_after = Pt(10)

    scenarios = [
        ("1. Conservador (10% Retención Salvada): ", "10.4 clientes retenidos. Ingreso bruto anual protegido: $12.013.411 COP."),
        ("2. Base (20% Retención Salvada): ", "20.8 clientes retenidos. Ingreso bruto anual protegido: $24.026.821 COP."),
        ("3. Optimista (30% Retención Salvada): ", "31.1 clientes retenidos. Ingreso bruto anual protegido: $36.040.232 COP."),
        ("Estrategia Ultra-Selectiva (Top 500 D1): ", "Concentrando el 65% del churn con costo promedio de $12.500 COP, el Escenario Base genera un ROI neto de +1.92x y protege el margen con total eficiencia operativa.")
    ]
    for s_title, s_desc in scenarios:
        p_b = tf2.add_paragraph()
        p_b.font.size = Pt(11)
        p_b.space_after = Pt(8)
        run1 = p_b.add_run()
        run1.text = s_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = s_desc
        run2.font.color.rgb = SLATE_GRAY


# ==============================================================================
# 10. BLUEPRINT EN AZURE DATABRICKS
# ==============================================================================
def build_slide_10(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "Blueprint Tecnológico: Industrialización en Azure Databricks", "Arquitectura Empresarial en la Nube de Claro", 10)

    # 4 Cuadros de Arquitectura
    box_w = Inches(2.7)
    box_h = Inches(5.0)

    col_data = [
        ("1. Medallion Delta Lake", DARK_NAVY, [
            ("Bronze: ", "Auto Loader ingiere facturación SAP, telemetría OSS de módems y transcripciones de IVR."),
            ("Silver: ", "DLT con expectativas de calidad y validación estricta de fuga T0. Feature Store Customer 360."),
            ("Gold: ", "Deciles de riesgo, recomendaciones y bitácora de auditoría.")
        ]),
        ("2. MLflow & UC", CLARO_RED, [
            ("Model Registry: ", "Firmas estrictas en Unity Catalog para Modelos A y B."),
            ("Lineage End-to-End: ", "Trazabilidad desde el módem del cliente hasta la decisión de cuadrilla."),
            ("Privacidad: ", "Dynamic Column Masking para Habeas Data.")
        ]),
        ("3. Databricks Workflows", BLUE_ACCENT, [
            ("Orquestación DAG: ", "Disparo programado a las 02:00 AM para scoring distribuido de millones de abonados."),
            ("Inferencia Spark: ", "Cálculo masivo de SHAP y deciles con pyfunc."),
            ("Reverse ETL: ", "Sincronización hacia Salesforce y Siebel.")
        ]),
        ("4. Observabilidad MLOps", GREEN_TEXT, [
            ("Lakehouse Monitoring: ", "Alerta semanal de Data Drift (PSI > 0.15) en variables SHAP críticas."),
            ("Concept Drift: ", "Evaluación mensual de degradación de PR-AUC."),
            ("HITL Metrics: ", "Supervisión de latencia p95 (<750ms) y tasa de override.")
        ])
    ]

    for idx, (col_title, title_color, col_bullets) in enumerate(col_data):
        c_left = Inches(0.8 + idx * 2.95)
        add_card(slide, c_left, Inches(1.6), box_w, box_h)
        tb = slide.shapes.add_textbox(c_left + Inches(0.2), Inches(1.8), box_w - Inches(0.4), box_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = col_title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = title_color
        p.space_after = Pt(10)

        for b_t, b_d in col_bullets:
            p_b = tf.add_paragraph()
            p_b.font.size = Pt(10)
            p_b.space_after = Pt(8)
            r1 = p_b.add_run()
            r1.text = b_t
            r1.font.bold = True
            r1.font.color.rgb = DARK_NAVY
            r2 = p_b.add_run()
            r2.text = b_d
            r2.font.color.rgb = SLATE_GRAY


# ==============================================================================
# 11. CONCLUSIÓN EJECUTIVA Y HOJA DE RUTA
# ==============================================================================
def build_slide_11(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "Conclusión Ejecutiva y Hoja de Ruta: Por qué esta Solución Transforma a Claro", "Cierre Estratégico de la Sustentación", 11)

    # Card 1: Pilares de Éxito
    add_card(slide, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
    tb1 = slide.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p1 = tf1.paragraphs[0]
    p1.text = "Diferenciadores Técnicos y de Negocio"
    p1.font.size = Pt(15)
    p1.font.bold = True
    p1.font.color.rgb = DARK_NAVY
    p1.space_after = Pt(10)

    bullets1 = [
        ("Honestidad Estadística Absoluta: ", "Sin trucos de data leakage T0. Modelos validados con 20 evaluaciones cruzadas, Lift de 9.05x y estimación económica basada en deciles reales."),
        ("Superación del Enfoque Reactivo: ", "Se descubrió y resolvió el 'Silent Churn Gap', blindando el 50% de las bajas que antes se perdían sin previo aviso."),
        ("Gobernanza Causal Estricta: ", "El sistema no regala dinero corporativo: asigna soluciones de ingeniería a problemas técnicos y ofertas comerciales a presiones tarifarias."),
        ("Diseño Industrial Ready: ", "Arquitectura lista para desplegar en Azure Databricks con gobierno Unity Catalog y protocolo FastMCP.")
    ]
    for b_title, b_desc in bullets1:
        p_b = tf1.add_paragraph()
        p_b.font.size = Pt(11)
        p_b.space_after = Pt(8)
        run1 = p_b.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = b_desc
        run2.font.color.rgb = SLATE_GRAY

    # Card 2: Hoja de Ruta 90 Días
    add_card(slide, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0))
    tb2 = slide.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.5))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p2 = tf2.paragraphs[0]
    p2.text = "Hoja de Ruta de Implementación (90 Días)"
    p2.font.size = Pt(15)
    p2.font.bold = True
    p2.font.color.rgb = CLARO_RED
    p2.space_after = Pt(10)

    steps = [
        ("Mes 1: Shadow Ingestion en Databricks: ", "Conexión de tablas Delta Bronze/Silver, registro de Modelos A y B en MLflow y pipeline de scoring silencioso diario."),
        ("Mes 2: Despliegue de la Bandeja HITL: ", "Lanzamiento de Databricks App para la mesa de supervisores senior de Claro en Cluster 3. Auditoría de feedback."),
        ("Mes 3: Piloto A/B en Cuadrillas Técnicas: ", "Despacho automatizado de visitas prioritarias y upgrades de velocidad vs grupo de control tradicional. Medición de retención real a 60 días."),
        ("Compromiso Personal: ", "Liderar con rigor analítico, transparencia metodológica y enfoque implacable en valor de negocio para Claro Colombia.")
    ]
    for s_title, s_desc in steps:
        p_b = tf2.add_paragraph()
        p_b.font.size = Pt(11)
        p_b.space_after = Pt(8)
        run1 = p_b.add_run()
        run1.text = s_title
        run1.font.bold = True
        run1.font.color.rgb = DARK_NAVY
        run2 = p_b.add_run()
        run2.text = s_desc
        run2.font.color.rgb = SLATE_GRAY


def main():
    print("Generando presentación ejecutiva en PowerPoint (16:9)...")
    prs = create_base_presentation()
    
    build_slide_1(prs)
    build_slide_2(prs)
    build_slide_3(prs)
    build_slide_4(prs)
    build_slide_5(prs)
    build_slide_6(prs)
    build_slide_7(prs)
    build_slide_8(prs)
    build_slide_9(prs)
    build_slide_10(prs)
    build_slide_11(prs)

    output_path = "presentacion/sustentacion_claro.pptx"
    prs.save(output_path)
    print(f"Presentación generada exitosamente en {output_path} (11 diapositivas)")


if __name__ == "__main__":
    main()
