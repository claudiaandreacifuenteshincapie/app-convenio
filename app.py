import streamlit as st
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Configuración de página
st.set_page_config(
    page_title="Dashboard Financiero - Convenio 4600017482",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS Profesionales (Mayor legibilidad y mejores colores)
st.markdown("""
    <style>
    /* Fondo principal y tipografía general */
    .stApp { background-color: #F8FAFC; }
    
    /* Contenedor de encabezado */
    .header-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        padding: 24px;
        border-radius: 16px;
        color: #FFFFFF;
        margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.15);
    }
    .header-title { font-size: 2.2rem; font-weight: 800; margin: 0; color: #FFFFFF; }
    .header-subtitle { font-size: 1rem; color: #93C5FD; margin-top: 5px; font-weight: 500; }
    
    /* Tarjetas Metricas */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-label { font-size: 0.85rem; color: #475569; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 1.8rem; font-weight: 800; margin-top: 8px; }
    
    /* Pestañas estilizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        color: #334155;
        border: 1px solid #E2E8F0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-color: #2563EB !important;
    }
    </style>
""", unsafe_allow_html=True)

# ENCABEZADO
st.markdown("""
    <div class="header-container">
        <p class="header-title">📊 Seguimiento Financiero - Convenio 4600017482</p>
        <p class="header-subtitle">Transformación Digital Salud Antioquia | Control Integrado de Pagos y Ejecucción</p>
    </div>
""", unsafe_allow_html=True)

# PRESUPUESTOS OFICIALES ATARREZADOS (Informe No. 22)
PRESUPUESTOS = {
    "1. Componente CAS (Salud)": 25982939387.0,
    "2. Componente CRUE (Otrosí)": 1462022598.0,
    "3. Consolidado General Convenio": 27444961985.0
}

# Carga de archivo desde barra lateral
st.sidebar.header("📁 Base de Datos Excel")
archivo_excel = st.sidebar.file_uploader("Sube tu archivo base (.xlsx):", type=["xlsx"])

# Datos por defecto (Últimos pagos registrados)
pagos_informe_recientes = [
    {"Componente": "1. Componente CAS (Salud)", "Factura": "Acumulado Base CAS", "Fecha": "2026-07-31", "Concepto": "Ejecución Acumulada Previa CAS", "Valor": 14905908982.0},
    {"Componente": "2. Componente CRUE (Otrosí)", "Factura": "Pago No. 50", "Fecha": "2026-08-01", "Concepto": "Autorización CRUE - Pago 50", "Valor": 27568325.0},
    {"Componente": "2. Componente CRUE (Otrosí)", "Factura": "Pago No. 51", "Fecha": "2026-08-15", "Concepto": "Autorización CRUE - Pago 51", "Valor": 2624505.0}
]

if "historico_pagos" not in st.session_state:
    st.session_state.historico_pagos = pd.DataFrame()

if archivo_excel is not None:
    try:
        df_excel = pd.read_excel(archivo_excel)
        df_informe = pd.DataFrame(pagos_informe_recientes)
        st.session_state.historico_pagos = pd.concat([df_excel, df_informe], ignore_index=True).drop_duplicates()
        st.sidebar.success("¡Excel cargado con éxito!")
    except Exception:
        st.sidebar.error("Error al leer el archivo Excel.")
elif st.session_state.historico_pagos.empty:
    try:
        df_local = pd.read_excel("historico_pagos.xlsx")
        df_informe = pd.DataFrame(pagos_informe_recientes)
        st.session_state.historico_pagos = pd.concat([df_local, df_informe], ignore_index=True).drop_duplicates()
    except:
        st.session_state.historico_pagos = pd.DataFrame(pagos_informe_recientes)

# SELECCIÓN DE COMPONENTE
st.subheader("1️⃣ Componente a Consultar")
componente_sel = st.radio(
    "Selecciona el módulo:",
    options=list(PRESUPUESTOS.keys()),
    horizontal=True
)

st.markdown("<br>", unsafe_allow_html=True)

# CÁLCULOS
presupuesto_total = PRESUPUESTOS[componente_sel]

if componente_sel == "3. Consolidado General Convenio":
    df_modulo = st.session_state.historico_pagos.copy()
else:
    df_modulo = st.session_state.historico_pagos[
        st.session_state.historico_pagos["Componente"] == componente_sel
    ] if not st.session_state.historico_pagos.empty else pd.DataFrame()

total_ejecutado = df_modulo["Valor"].sum() if not df_modulo.empty else 0.0
saldo_disponible = presupuesto_total - total_ejecutado
pct_ejecucion = (total_ejecutado / presupuesto_total * 100) if presupuesto_total > 0 else 0.0

# TARJETAS DE MÉTRICAS Y GRÁFICO PEQUEÑO
col_m1, col_m2, col_m3, col_g = st.columns([1, 1, 1, 1.2])

with col_m1:
    st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #2563EB;">
            <div class="metric-label">Presupuesto Asignado</div>
            <div class="metric-value" style="color: #1E293B;">${presupuesto_total:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with col_m2:
    color_ejec = "#059669" if total_ejecutado <= presupuesto_total else "#DC2626"
    st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid {color_ejec};">
            <div class="metric-label">Total Ejecutado ({pct_ejecucion:.1f}%)</div>
            <div class="metric-value" style="color: {color_ejec};">${total_ejecutado:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with col_m3:
    color_saldo = "#059669" if saldo_disponible >= 0 else "#DC2626"
    st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid {color_saldo};">
            <div class="metric-label">Saldo Disponible Real</div>
            <div class="metric-value" style="color: {color_saldo};">${saldo_disponible:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

# GRÁFICO PEQUEÑO COMPACTO (Donut Chart)
with col_g:
    labels = ['Ejecutado', 'Disponible']
    values = [max(total_ejecutado, 0), max(saldo_disponible, 0)]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=.6,
        marker_colors=['#2563EB', '#10B981'],
        textinfo='percent',
        showlegend=False
    )])
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        height=120,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# NAVEGACIÓN EN PESTAÑAS PARA ORDENAR LA INFORMACIÓN
tab1, tab2 = st.tabs(["📋 Histórico Completo y Exportación", "➕ Registrar Nuevo Pago"])

with tab1:
    if not df_modulo.empty:
        df_display = df_modulo.copy()
        df_display["Valor Formateado"] = df_display["Valor"].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00")
        
        cols_mostrar = [c for c in ["Componente", "Factura", "Fecha", "Concepto", "Valor Formateado"] if c in df_display.columns]
        st.dataframe(df_display[cols_mostrar], use_container_width=True, height=350)

        # Generador de Excel
        def generar_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Historico_Pagos')
            return output.getvalue()

        # Generador de PDF
        def generar_pdf(df, componente, presupuesto, ejecutado, saldo):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph(f"<b>Reporte Financiero - Convenio 4600017482</b>", styles['Title']))
            elements.append(Paragraph(f"<b>Módulo:</b> {componente}", styles['Heading2']))
            elements.append(Spacer(1, 10))

            resumen_data = [
                ["Presupuesto Asignado", "Total Ejecutado", "Saldo Disponible"],
                [f"${presupuesto:,.0f}", f"${ejecutado:,.0f}", f"${saldo:,.0f}"]
            ]
            resumen_table = Table(resumen_data, colWidths=[180, 180, 180])
            resumen_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F8FAFC')),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0'))
            ]))
            elements.append(resumen_table)
            elements.append(Spacer(1, 20))

            elements.append(Paragraph("<b>Detalle Histórico de Pagos</b>", styles['Heading3']))
            tabla_data = [["Componente", "Factura", "Fecha", "Concepto", "Valor ($)"]]
            for _, row in df.iterrows():
                tabla_data.append([
                    str(row.get('Componente', '')),
                    str(row.get('Factura', '')),
                    str(row.get('Fecha', '')),
                    str(row.get('Concepto', '')),
                    f"${row.get('Valor', 0):,.2f}"
                ])
            
            tabla = Table(tabla_data, colWidths=[120, 80, 70, 170, 100])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563EB')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,0), 4),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1'))
            ]))
            elements.append(tabla)

            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()

        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            excel_data = generar_excel(df_modulo)
            st.download_button(
                label="📥 Descargar Histórico Completo en Excel",
                data=excel_data,
                file_name=f"historico_completo_{componente_sel.split('.')[0]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col_dl2:
            pdf_data = generar_pdf(df_modulo, componente_sel, presupuesto_total, total_ejecutado, saldo_disponible)
            st.download_button(
                label="📄 Descargar Reporte en PDF",
                data=pdf_data,
                file_name=f"reporte_financiero_{componente_sel.split('.')[0]}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("No hay registros disponibles para el componente seleccionado.")

with tab2:
    with st.form("form_nuevo_pago", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            num_factura = st.text_input("Número / Referencia de Factura / Cuenta *")
            fecha_pago = st.date_input("Fecha de Pago")
            comp_factura = st.selectbox("Componente Asignado", options=list(PRESUPUESTOS.keys()), index=list(PRESUPUESTOS.keys()).index(componente_sel))
        
        with col2:
            concepto = st.text_input("Concepto / Descripción *")
            valor_pago = st.number_input("Valor del Pago ($ COP) *", min_value=0.0, step=100000.0, format="%.2f")
        
        btn_guardar = st.form_submit_button("💾 Registrar Pago y Actualizar Saldo")

        if btn_guardar:
            if not num_factura or valor_pago <= 0 or not concepto:
                st.warning("⚠️ Completa todos los campos obligatorios.")
            else:
                nuevo_registro = pd.DataFrame([{
                    "Componente": comp_factura,
                    "Factura": num_factura,
                    "Fecha": str(fecha_pago),
                    "Concepto": concepto,
                    "Valor": valor_pago
                }])
                st.session_state.historico_pagos = pd.concat([st.session_state.historico_pagos, nuevo_registro], ignore_index=True)
                st.success(f"🎉 ¡Pago registrado con éxito por ${valor_pago:,.2f}!")
