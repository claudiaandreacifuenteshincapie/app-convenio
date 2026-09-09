import streamlit as st
import pandas as pd
import os
import io

# Librerías para generación de PDF
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuración de página
st.set_page_config(
    page_title="Seguimiento Financiero - Convenio 4600017482",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .main-title { color: #1E3A8A; font-size: 2.2rem; font-weight: 700; margin-bottom: 0px; }
    .sub-title { color: #4B5563; font-size: 1rem; margin-bottom: 25px; }
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #2563EB;
        margin-bottom: 15px;
    }
    .metric-label { font-size: 0.85rem; color: #6B7280; font-weight: 600; text-transform: uppercase; }
    .metric-value { font-size: 1.7rem; font-weight: 700; color: #111827; margin-top: 5px; }
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
    }
    .stButton>button {
        background-color: #2563EB; color: white; border-radius: 8px;
        font-weight: 600; border: none; padding: 10px 24px;
    }
    .stButton>button:hover { background-color: #1D4ED8; color: white; }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown('<p class="main-title">📊 Seguimiento Financiero - Convenio 4600017482</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Transformación Digital Salud Antioquia | Descarga de Reportes en Excel y PDF</p>', unsafe_allow_html=True)

# Presupuestos base
PRESUPUESTOS = {
    "1. Componente CAS (Salud)": 25982939387,
    "2. Componente CRUE (Otrosí)": 5000000000,
    "3. Banco IDEA / Rendimientos": 1200000000
}

def sanear_dataframe(df):
    if df.empty:
        return df
    nuevas_columnas = []
    for i, col in enumerate(df.columns):
        if pd.isna(col) or str(col).strip() == "" or "Unnamed" in str(col):
            nuevas_columnas.append(f"Columna_{i+1}")
        else:
            nuevas_columnas.append(str(col).strip())
    df.columns = nuevas_columnas
    df = df.fillna("")
    return df

@st.cache_data(ttl=5)
def cargar_y_limpiar_excel():
    archivos = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not archivos:
        return pd.DataFrame(), None
    
    file_path = archivos[0]
    try:
        df_raw = pd.read_excel(file_path)
        for idx, row in df_raw.iterrows():
            row_str = row.astype(str).str.lower().to_list()
            if any('factura' in x or 'concepto' in x or 'valor' in x or 'pago' in x for x in row_str):
                df_raw.columns = df_raw.iloc[idx]
                df_raw = df_raw.iloc[idx + 1:].reset_index(drop=True)
                break

        if not df_raw.empty and len(df_raw.columns) > 0:
            col_0 = df_raw.columns[0]
            df_raw = df_raw[~df_raw[col_0].astype(str).str.upper().str.contains("TOTAL", na=False)]
        
        df_raw = sanear_dataframe(df_raw)
        return df_raw, file_path
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        return pd.DataFrame(), None

df_excel, nombre_archivo = cargar_y_limpiar_excel()

if "pagos_nuevos" not in st.session_state:
    st.session_state.pagos_nuevos = pd.DataFrame(columns=["Componente", "Factura", "Fecha", "Concepto", "Valor"])

if nombre_archivo:
    st.success(f"🟢 Datos conectados desde: **{nombre_archivo}**")

# ----------------------------------------------------
# SECCIÓN 1: SELECCIÓN DE COMPONENTE
# ----------------------------------------------------
st.subheader("1️⃣ Selección de Componente a Consultar")
componente_sel = st.radio(
    "Selecciona el módulo financiero:",
    options=list(PRESUPUESTOS.keys()),
    horizontal=True
)

st.markdown("---")

# ----------------------------------------------------
# SECCIÓN 2: FORMULARIO DE INGRESO
# ----------------------------------------------------
st.subheader("➕ Registrar Nuevo Pago / Factura")

with st.form("form_nuevo_pago", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        num_factura = st.text_input("Número / Referencia de Factura *")
        fecha_pago = st.date_input("Fecha de Pago")
        comp_factura = st.selectbox("Componente Asignado", options=list(PRESUPUESTOS.keys()), index=list(PRESUPUESTOS.keys()).index(componente_sel))
    
    with col2:
        concepto = st.text_input("Concepto / Descripción *")
        valor_pago = st.number_input("Valor del Pago ($ COP) *", min_value=0.0, step=500000.0, format="%.2f")
    
    btn_guardar = st.form_submit_button("💾 Añadir Pago y Recalcular")

    if btn_guardar:
        if not num_factura or valor_pago <= 0 or not concepto:
            st.warning("⚠️ Completa los campos obligatorios: número de factura, concepto y valor mayor a cero.")
        else:
            nuevo_registro = pd.DataFrame([{
                "Componente": comp_factura,
                "Factura": num_factura,
                "Fecha": str(fecha_pago),
                "Concepto": concepto,
                "Valor": str(valor_pago)
            }])
            st.session_state.pagos_nuevos = pd.concat([st.session_state.pagos_nuevos, nuevo_registro], ignore_index=True)
            st.success(f"🎉 ¡Pago por ${valor_pago:,.2f} registrado con éxito!")

st.markdown("---")

# ----------------------------------------------------
# SECCIÓN 3: MÉTRICAS
# ----------------------------------------------------
df_consolidado = pd.concat([df_excel, st.session_state.pagos_nuevos], ignore_index=True)
df_consolidado = sanear_dataframe(df_consolidado)

col_valor = None
for c in df_consolidado.columns:
    if any(term in str(c).lower() for term in ['valor', 'monto', 'ejecutado', 'pago', 'columna_4', 'columna_3']):
        col_valor = c
        break

if col_valor:
    df_consolidado['Valor_Limpio'] = pd.to_numeric(
        df_consolidado[col_valor].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False),
        errors='coerce'
    ).fillna(0)
else:
    df_consolidado['Valor_Limpio'] = 0.0

col_comp = None
for c in df_consolidado.columns:
    if any(term in str(c).lower() for term in ['componente', 'modulo', 'convenio']):
        col_comp = c
        break

if col_comp:
    filtro_key = componente_sel.split('.')[1].strip().split(' ')[0]
    df_filtrado = df_consolidado[df_consolidado[col_comp].astype(str).str.contains(filtro_key, case=False, na=False)]
else:
    df_filtrado = df_consolidado

presupuesto_total = PRESUPUESTOS[componente_sel]
total_ejecutado = df_filtrado['Valor_Limpio'].sum()
saldo_disponible = presupuesto_total - total_ejecutado
pct_ejecucion = (total_ejecutado / presupuesto_total * 100) if presupuesto_total > 0 else 0.0

st.subheader(f"📈 Métricas Calculadas: {componente_sel}")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #2563EB;">
            <div class="metric-label">Presupuesto Asignado</div>
            <div class="metric-value">${presupuesto_total:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    color_ejecutado = "#059669" if total_ejecutado <= presupuesto_total else "#DC2626"
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: {color_ejecutado};">
            <div class="metric-label">Total Ejecutado Real ({pct_ejecucion:.1f}%)</div>
            <div class="metric-value" style="color: {color_ejecutado};">${total_ejecutado:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    color_saldo = "#059669" if saldo_disponible >= 0 else "#DC2626"
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: {color_saldo};">
            <div class="metric-label">Saldo Disponible</div>
            <div class="metric-value" style="color: {color_saldo};">${saldo_disponible:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

st.progress(min(max(pct_ejecucion / 100, 0.0), 1.0))

st.markdown("---")

# ----------------------------------------------------
# SECCIÓN 4: TABLA Y DESCARGA EXCEL / PDF
# ----------------------------------------------------
st.subheader("📋 Detalle de Registros")

df_tabla = df_consolidado.drop(columns=['Valor_Limpio'], errors='ignore').astype(str)
st.dataframe(df_tabla, use_container_width=True)

col_d1, col_d2 = st.columns(2)

# 1. Generación de Excel
buffer_excel = io.BytesIO()
with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
    df_tabla.to_excel(writer, index=False, sheet_name='Reporte_Pagos')
data_excel = buffer_excel.getvalue()

with col_d1:
    st.download_button(
        label="📊 Descargar Reporte en Excel (.xlsx)",
        data=data_excel,
        file_name='reporte_convenio_4600017482.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )

# 2. Generación de PDF
def generar_pdf(df, componente, p_total, ejecutado, saldo):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=15
    )
    
    story.append(Paragraph("<b>Reporte de Seguimiento Financiero - Convenio 4600017482</b>", title_style))
    story.append(Paragraph(f"<b>Componente:</b> {componente} | Transformación Digital Salud Antioquia", subtitle_style))
    
    # Resumen Ejecutivo
    resumen_data = [
        ["Presupuesto Asignado", "Total Ejecutado", "Saldo Disponible"],
        [f"${p_total:,.0f}", f"${ejecutado:,.0f}", f"${saldo:,.0f}"]
    ]
    t_resumen = Table(resumen_data, colWidths=[240, 240, 240])
    t_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563EB')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F3F4F6')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#D1D5DB')),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    story.append(t_resumen)
    story.append(Spacer(1, 15))
    
    # Tabla de Registros (Limitada a las primeras 10 columnas si hay muchas)
    cols_pdf = list(df.columns)[:8]
    df_pdf = df[cols_pdf]
    
    table_data = [cols_pdf] + df_pdf.values.tolist()
    # Recortar textos largos para que quepan bien
    table_data_clean = []
    for row in table_data:
        new_row = [str(cell)[:35] + ("..." if len(str(cell)) > 35 else "") for cell in row]
        table_data_clean.append(new_row)

    t_detalle = Table(table_data_clean, repeatRows=1)
    t_detalle.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
    ]))
    story.append(t_detalle)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

try:
    pdf_bytes = generar_pdf(df_tabla, componente_sel, presupuesto_total, total_ejecutado, saldo_disponible)
    with col_d2:
        st.download_button(
            label="📄 Descargar Reporte en PDF (.pdf)",
            data=pdf_bytes,
            file_name='reporte_convenio_4600017482.pdf',
            mime='application/pdf',
        )
except Exception as e:
    with col_d2:
        st.warning(f"No se pudo construir el PDF: {e}")
