import streamlit as st
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
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
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown('<p class="main-title">📊 Seguimiento Financiero - Convenio 4600017482</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Transformación Digital Salud Antioquia | Cifras Aterrizadas e Histórico Completo</p>', unsafe_allow_html=True)

# PRESUPUESTOS OFICIALES ATARREZADOS (Informe No. 22)
PRESUPUESTOS = {
    "1. Componente CAS (Salud)": 25982939387.0,
    "2. Componente CRUE (Otrosí)": 1462022598.0,
    "3. Consolidado General Convenio": 27444961985.0
}

# Cargar/Inicializar la base de datos completa (Consolidando Excel anterior + Informe 22)
if "historico_pagos" not in st.session_state:
    st.session_state.historico_pagos = pd.DataFrame([
        # Base inicial del Excel que ya teníamos adelantada (Componente CAS)
        {"Componente": "1. Componente CAS (Salud)", "Factura": "Acumulado Base CAS", "Fecha": "2026-07-31", "Concepto": "Ejecución Acumulada Previa CAS", "Valor": 14905908982.0},
        
        # Histórico de Pagos y Autorizaciones CRUE (Informe No. 22)
        {"Componente": "2. Componente CRUE (Otrosí)", "Factura": "Pago No. 50", "Fecha": "2026-08-01", "Concepto": "Autorización CRUE - Pago 50", "Valor": 27568325.0},
        {"Componente": "2. Componente CRUE (Otrosí)", "Factura": "Pago No. 51", "Fecha": "2026-08-15", "Concepto": "Autorización CRUE - Pago 51", "Valor": 2624505.0}
    ])

# 1️⃣ SELECCIÓN DE COMPONENTE
st.subheader("1️⃣ Selección de Componente a Consultar")
componente_sel = st.radio(
    "Selecciona el módulo financiero:",
    options=list(PRESUPUESTOS.keys()),
    horizontal=True
)

st.markdown("---")

# 2️⃣ FORMULARIO PARA AGREGAR NUEVOS PAGOS
st.subheader("➕ Registrar Nuevo Pago / Factura")
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
            st.warning("⚠️ Por favor completa todos los campos obligatorios.")
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

st.markdown("---")

# 3️⃣ CÁLCULOS Y MÉTRICAS
presupuesto_total = PRESUPUESTOS[componente_sel]

# Filtrado dinámico según la pestaña seleccionada
if componente_sel == "3. Consolidado General Convenio":
    df_modulo = st.session_state.historico_pagos.copy()
else:
    df_modulo = st.session_state.historico_pagos[
        st.session_state.historico_pagos["Componente"] == componente_sel
    ]

total_ejecutado = df_modulo["Valor"].sum() if not df_modulo.empty else 0.0
saldo_disponible = presupuesto_total - total_ejecutado
pct_ejecucion = (total_ejecutado / presupuesto_total * 100) if presupuesto_total > 0 else 0.0

st.subheader(f"📈 Métricas Realistas: {componente_sel}")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #2563EB;">
            <div class="metric-label">Presupuesto Asignado</div>
            <div class="metric-value">${presupuesto_total:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    color_ejec = "#059669" if total_ejecutado <= presupuesto_total else "#DC2626"
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: {color_ejec};">
            <div class="metric-label">Total Ejecutado ({pct_ejecucion:.2f}%)</div>
            <div class="metric-value" style="color: {color_ejec};">${total_ejecutado:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    color_saldo = "#059669" if saldo_disponible >= 0 else "#DC2626"
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: {color_saldo};">
            <div class="metric-label">Saldo Disponible Real</div>
            <div class="metric-value" style="color: {color_saldo};">${saldo_disponible:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

st.progress(min(max(pct_ejecucion / 100, 0.0), 1.0))

st.markdown("---")

# 4️⃣ HISTÓRICO VISIBLE Y DESCARGAS (EXCEL Y PDF)
st.subheader("📋 Histórico Completo de Pagos y Descarga")

if not df_modulo.empty:
    # Muestra el histórico formateado con las cifras de los pagos
    df_display = df_modulo.copy()
    df_display["Valor Formateado"] = df_display["Valor"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(df_display[["Componente", "Factura", "Fecha", "Concepto", "Valor Formateado"]], use_container_width=True)

    # Función para generar Excel
    def generar_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Historico_Pagos')
        return output.getvalue()

    # Función para generar PDF
    def generar_pdf(df, componente, presupuesto, ejecutado, saldo):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph(f"<b>Reporte Financiero - Convenio 4600017482</b>", styles['Title']))
        elements.append(Paragraph(f"<b>Módulo:</b> {componente}", styles['Heading2']))
        elements.append(Spacer(1, 10))

        # Cuadro resumido
        resumen_data = [
            ["Presupuesto Asignado", "Total Ejecutado", "Saldo Disponible"],
            [f"${presupuesto:,.0f}", f"${ejecutado:,.0f}", f"${saldo:,.0f}"]
        ]
        resumen_table = Table(resumen_data, colWidths=[180, 180, 180])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F3F4F6')),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#D1D5DB'))
        ]))
        elements.append(resumen_table)
        elements.append(Spacer(1, 20))

        # Detalle de Pagos
        elements.append(Paragraph("<b>Detalle Histórico de Pagos</b>", styles['Heading3']))
        tabla_data = [["Componente", "Factura", "Fecha", "Concepto", "Valor ($)"]]
        for _, row in df.iterrows():
            tabla_data.append([
                str(row['Componente']),
                str(row['Factura']),
                str(row['Fecha']),
                str(row['Concepto']),
                f"${row['Valor']:,.2f}"
            ])
        
        tabla = Table(tabla_data, colWidths=[120, 80, 70, 170, 100])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563EB')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB'))
        ]))
        elements.append(tabla)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        excel_data = generar_excel(df_modulo)
        st.download_button(
            label="📥 Descargar Histórico en Excel",
            data=excel_data,
            file_name=f"historico_pagos_{componente_sel.split('.')[0]}.xlsx",
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
