import streamlit as st
import pandas as pd
import os
import io

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
st.markdown('<p class="sub-title">Transformación Digital Salud Antioquia | Cifras Oficiales Actualizadas</p>', unsafe_allow_html=True)

# PRESUPUESTOS Y EJECUCIÓN BASE OFICIAL (Informe 22)
DATOS_OFICIALES = {
    "1. Componente CAS (Salud)": {
        "presupuesto": 25982939387,
        "ejecutado_base": 14905908982
    },
    "2. Componente CRUE (Otrosí)": {
        "presupuesto": 1462022598,  # Valor de adición / componentes específicos CRUE
        "ejecutado_base": 30192830    # Pagos No. 50 y 51 autorizados
    },
    "3. Consolidado General Convenio": {
        "presupuesto": 27444961985,
        "ejecutado_base": 14936101812
    }
}

# Selección de módulo
st.subheader("1️⃣ Selección de Componente a Consultar")
componente_sel = st.radio(
    "Selecciona el módulo financiero:",
    options=list(DATOS_OFICIALES.keys()),
    horizontal=True
)

st.markdown("---")

# Manejo de registros adicionales ingresados manualmente en la sesión
if "pagos_nuevos" not in st.session_state:
    st.session_state.pagos_nuevos = pd.DataFrame(columns=["Componente", "Factura", "Fecha", "Concepto", "Valor"])

# Formulario para ingresar nuevos pagos el próximo mes
st.subheader("➕ Registrar Nuevo Pago / Factura")
with st.form("form_nuevo_pago", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        num_factura = st.text_input("Número / Referencia de Factura / Cuenta *")
        fecha_pago = st.date_input("Fecha de Pago")
        comp_factura = st.selectbox("Componente Asignado", options=list(DATOS_OFICIALES.keys()), index=list(DATOS_OFICIALES.keys()).index(componente_sel))
    
    with col2:
        concepto = st.text_input("Concepto / Descripción *")
        valor_pago = st.number_input("Valor del Pago ($ COP) *", min_value=0.0, step=100000.0, format="%.2f")
    
    btn_guardar = st.form_submit_button("💾 Registrar Pago y Actualizar Saldo")

    if btn_guardar:
        if not num_factura or valor_pago <= 0 or not concepto:
            st.warning("⚠️ Completa los campos obligatorios.")
        else:
            nuevo_registro = pd.DataFrame([{
                "Componente": comp_factura,
                "Factura": num_factura,
                "Fecha": str(fecha_pago),
                "Concepto": concepto,
                "Valor": valor_pago
            }])
            st.session_state.pagos_nuevos = pd.concat([st.session_state.pagos_nuevos, nuevo_registro], ignore_index=True)
            st.success(f"🎉 Pago registrado por ${valor_pago:,.2f}!")

st.markdown("---")

# CÁLCULOS DE SALDOS Y MÉTRICAS
datos_comp = DATOS_OFICIALES[componente_sel]
presupuesto_total = datos_comp["presupuesto"]
ejecutado_acumulado_informe = datos_comp["ejecutado_base"]

# Sumar pagos nuevos agregados manualmente en el componente seleccionado
pagos_nuevos_comp = st.session_state.pagos_nuevos[
    st.session_state.pagos_nuevos["Componente"] == componente_sel
]["Valor"].sum() if not st.session_state.pagos_nuevos.empty else 0.0

total_ejecutado_real = ejecutado_acumulado_informe + pagos_nuevos_comp
saldo_disponible = presupuesto_total - total_ejecutado_real
pct_ejecucion = (total_ejecutado_real / presupuesto_total * 100) if presupuesto_total > 0 else 0.0

st.subheader(f"📈 Métricas Realistas a la Fecha: {componente_sel}")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: #2563EB;">
            <div class="metric-label">Presupuesto Asignado</div>
            <div class="metric-value">${presupuesto_total:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    color_ejec = "#059669" if total_ejecutado_real <= presupuesto_total else "#DC2626"
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: {color_ejec};">
            <div class="metric-label">Total Ejecutado ({pct_ejecucion:.2f}%)</div>
            <div class="metric-value" style="color: {color_ejec};">${total_ejecutado_real:,.0f}</div>
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

# Tabla de nuevos registros
if not st.session_state.pagos_nuevos.empty:
    st.subheader("📋 Registros Adicionales Ingresados este Mes")
    st.dataframe(st.session_state.pagos_nuevos, use_container_width=True)
