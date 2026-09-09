import streamlit as st
import pandas as pd
import os

# Configuración de página
st.set_page_config(
    page_title="Seguimiento Financiero - Convenio 4600017482",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS Personalizados
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
st.markdown('<p class="main-title">📊 Seguimiento Financiero en Tiempo Real - Convenio 4600017482</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Transformación Digital Salud Antioquia | Lectura en vivo desde Excel + Control de Pagos</p>', unsafe_allow_html=True)

# Presupuestos base
PRESUPUESTOS = {
    "1. Componente CAS (Salud)": 25982939387,
    "2. Componente CRUE (Otrosí)": 5000000000,
    "3. Banco IDEA / Rendimientos": 1200000000
}

# Función para cargar datos reales desde el archivo de Excel
@st.cache_data(ttl=5)
def cargar_excel_real():
    archivos = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if archivos:
        try:
            # Lee la primera hoja del Excel disponible en la carpeta
            df = pd.read_excel(archivos[0])
            return df, archivos[0]
        except Exception as e:
            return pd.DataFrame(), None
    return pd.DataFrame(), None

df_excel, nombre_archivo = cargar_excel_real()

if "pagos_nuevos" not in st.session_state:
    st.session_state.pagos_nuevos = pd.DataFrame(columns=["Componente", "Factura", "Fecha", "Concepto", "Valor"])

if nombre_archivo:
    st.success(f"🟢 Archivo conectado en tiempo real: **{nombre_archivo}**")
else:
    st.warning("⚠️ No se encontró el archivo Excel en el repositorio. Usando estructura base.")

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
# SECCIÓN 2: FORMULARIO RÁPIDO PARA NUEVOS PAGOS
# ----------------------------------------------------
st.subheader("➕ Registrar Nuevo Pago / Factura")

with st.form("form_nuevo_pago", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        num_factura = st.text_input("Número / Referencia de Factura *", placeholder="Ej: FAC-2026-001")
        fecha_pago = st.date_input("Fecha de Pago")
        comp_factura = st.selectbox("Componente Asignado", options=list(PRESUPUESTOS.keys()), index=list(PRESUPUESTOS.keys()).index(componente_sel))
    
    with col2:
        concepto = st.text_input("Concepto / Descripción *", placeholder="Ej: Abono o pago de acta mensual")
        valor_pago = st.number_input("Valor del Pago ($ COP) *", min_value=0.0, step=500000.0, format="%.2f")
    
    btn_guardar = st.form_submit_button("💾 Añadir Pago y Recalcular")

    if btn_guardar:
        if not num_factura or valor_pago <= 0 or not concepto:
            st.warning("⚠️ Completa los campos requeridos: número de factura, concepto y un valor mayor a cero.")
        else:
            nuevo_registro = pd.DataFrame([{
                "Componente": comp_factura,
                "Factura": num_factura,
                "Fecha": str(fecha_pago),
                "Concepto": concepto,
                "Valor": valor_pago
            }])
            st.session_state.pagos_nuevos = pd.concat([st.session_state.pagos_nuevos, nuevo_registro], ignore_index=True)
            st.success(f"🎉 ¡Pago registrado! Se agregaron ${valor_pago:,.2f} al componente.")

st.markdown("---")

# ----------------------------------------------------
# SECCIÓN 3: CONSOLIDACIÓN DE DATOS Y MÉTRICAS
# ----------------------------------------------------
# Mapeo y consolidación de datos del Excel con los Pagos Nuevos
df_total = df_excel.copy() if not df_excel.empty else pd.DataFrame()

# Normalización de columnas si existen en el Excel
if not df_total.empty:
    # Intenta identificar la columna del valor en el Excel
    cols_posibles_valor = [c for c in df_total.columns if 'valor' in str(c).lower() or 'monto' in str(c).lower() or 'ejecutado' in str(c).lower()]
    if cols_posibles_valor:
        df_total['Valor'] = pd.to_numeric(df_total[cols_posibles_valor[0]], errors='coerce').fillna(0)
    elif 'Valor' not in df_total.columns:
        df_total['Valor'] = 0.0

    # Intenta identificar la columna del componente
    cols_posibles_comp = [c for c in df_total.columns if 'componente' in str(c).lower() or 'modulo' in str(c).lower()]
    if cols_posibles_comp:
        df_total['Componente'] = df_total[cols_posibles_comp[0]]
    elif 'Componente' not in df_total.columns:
        df_total['Componente'] = componente_sel

# Unir histórico del Excel con nuevos pagos ingresados en la sesión
df_consolidado = pd.concat([df_total, st.session_state.pagos_nuevos], ignore_index=True)

# Filtro según componente seleccionado
df_filtrado = df_consolidado[df_consolidado["Componente"].astype(str).str.contains(componente_sel.split('.')[1].strip().split(' ')[0], case=False, na=False)] if "Componente" in df_consolidado.columns else df_consolidado

# Cálculos Presupuestales
presupuesto_total = PRESUPUESTOS[componente_sel]
total_ejecutado = df_filtrado["Valor"].sum() if not df_filtrado.empty and "Valor" in df_filtrado.columns else 0.0
saldo_disponible = presupuesto_total - total_ejecutado
pct_ejecucion = (total_ejecutado / presupuesto_total * 100) if presupuesto_total > 0 else 0.0

st.subheader(f"📈 Métricas en Tiempo Real: {componente_sel}")

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
# SECCIÓN 4: VISTA DE TABLA Y DESCARGA
# ----------------------------------------------------
st.subheader("📋 Detalle Consolidado de Pagos")

if not df_consolidado.empty:
    st.dataframe(df_consolidado, use_container_width=True)
    
    csv_data = df_consolidado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte Consolidado Actualizado (CSV)",
        data=csv_data,
        file_name='reporte_consolidado_convenio.csv',
        mime='text/csv',
    )
else:
    st.info("No hay datos para mostrar.")
