import streamlit as st
import pandas as pd
import os

# Configuración de página
st.set_page_config(
    page_title="Seguimiento Financiero - Convenio 4600017482",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS Personalizados para una interfaz más bonita
st.markdown("""
    <style>
    /* Fondo general suave */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Encabezado principal */
    .main-title {
        color: #1E3A8A;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #4B5563;
        font-size: 1rem;
        margin-bottom: 25px;
    }

    /* Tarjetas de Métricas */
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 5px solid #2563EB;
        margin-bottom: 15px;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #111827;
        margin-top: 5px;
    }
    
    /* Estilo del Formulario */
    div[data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
    }

    /* Botón personalizado */
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown('<p class="main-title">📊 Seguimiento Financiero - Convenio 4600017482</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Transformación Digital Salud Antioquia | Panel Control de Pagos y Facturación</p>', unsafe_allow_html=True)

# Presupuestos base
PRESUPUESTOS = {
    "1. Componente CAS (Salud)": 25982939387,
    "2. Componente CRUE (Otrosí)": 5000000000,
    "3. Banco IDEA / Rendimientos": 1200000000
}

# Carga de datos inicial con session_state
if "df_pagos" not in st.session_state:
    try:
        archivos = [f for f in os.listdir('.') if f.startswith('Seguimiento Financiero') and f.endswith('.xlsx')]
        if archivos:
            st.session_state.df_pagos = pd.read_excel(archivos[0])
        else:
            st.session_state.df_pagos = pd.DataFrame(columns=["Componente", "Factura", "Fecha", "Concepto", "Valor"])
    except Exception:
        st.session_state.df_pagos = pd.DataFrame(columns=["Componente", "Factura", "Fecha", "Concepto", "Valor"])

st.success("✨ Sistema cargado con éxito. Interfaz mejorada y lista para registro.")

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
# SECCIÓN 2: REGISTRO DE NUEVA FACTURA
# ----------------------------------------------------
st.subheader("➕ Registrar Nueva Factura / Pago")

with st.form("form_facturas", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        num_factura = st.text_input("Número / Referencia de Factura *", placeholder="Ej: F-12045")
        fecha_pago = st.date_input("Fecha de Factura / Pago")
        comp_factura = st.selectbox("Componente Asignado", options=list(PRESUPUESTOS.keys()), index=list(PRESUPUESTOS.keys()).index(componente_sel))
    
    with col2:
        concepto = st.text_input("Concepto / Descripción del Pago *", placeholder="Ej: Pago de servicios técnicos de software")
        valor_factura = st.number_input("Valor de la Factura ($ COP) *", min_value=0.0, step=1000000.0, format="%.2f")
    
    btn_guardar = st.form_submit_button("💾 Registar Factura y Recalcular Presupuesto")

    if btn_guardar:
        if not num_factura or valor_factura <= 0 or not concepto:
            st.warning("⚠️ Completa los campos obligatorios (*): número de factura, concepto y un valor mayor a cero.")
        else:
            nueva_factura = pd.DataFrame([{
                "Componente": comp_factura,
                "Factura": num_factura,
                "Fecha": str(fecha_pago),
                "Concepto": concepto,
                "Valor": valor_factura
            }])
            st.session_state.df_pagos = pd.concat([st.session_state.df_pagos, nueva_factura], ignore_index=True)
            st.success(f"🎉 Factura N° {num_factura} por ${valor_factura:,.2f} agregada exitosamente.")

st.markdown("---")

# ----------------------------------------------------
# SECCIÓN 3: CÁLCULOS Y TARJETAS DINÁMICAS
# ----------------------------------------------------
presupuesto_total = PRESUPUESTOS[componente_sel]

# Filtrar ejecuciones por el componente activo
df_filtrado = st.session_state.df_pagos[st.session_state.df_pagos["Componente"] == componente_sel] if "Componente" in st.session_state.df_pagos.columns else pd.DataFrame()

total_ejecutado = df_filtrado["Valor"].sum() if not df_filtrado.empty and "Valor" in df_filtrado.columns else 0.0
saldo_disponible = presupuesto_total - total_ejecutado
pct_ejecucion = (total_ejecutado / presupuesto_total * 100) if presupuesto_total > 0 else 0.0

st.subheader(f"📈 Resumen Ejecución: {componente_sel}")

# Mostrar Métricas en tarjetas estilizadas
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #2563EB;">
            <div class="metric-label">Valor Total Presupuesto</div>
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
# SECCIÓN 4: TABLA DE DATOS Y EXPORTACIÓN
# ----------------------------------------------------
st.subheader("📋 Registro Histórico de Facturas y Pagos")

if not df_filtrado.empty:
    st.dataframe(df_filtrado, use_container_width=True)
    
    csv = st.session_state.df_pagos.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte Completo (CSV)",
        data=csv,
        file_name='reporte_pagos_convenio.csv',
        mime='text/csv',
    )
else:
    st.info("Aún no hay facturas registradas para este componente.")
