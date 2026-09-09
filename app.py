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
st.markdown('<p class="sub-title">Transformación Digital Salud Antioquia | Descarga en Excel y Limpieza de Datos</p>', unsafe_allow_html=True)

# Presupuestos base
PRESUPUESTOS = {
    "1. Componente CAS (Salud)": 25982939387,
    "2. Componente CRUE (Otrosí)": 5000000000,
    "3. Banco IDEA / Rendimientos": 1200000000
}

@st.cache_data(ttl=5)
def cargar_y_limpiar_excel():
    archivos = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    if not archivos:
        return pd.DataFrame(), None
    
    file_path = archivos[0]
    df_raw = pd.read_excel(file_path)
    
    # Promover encabezados reales si existen
    for idx, row in df_raw.iterrows():
        row_str = row.astype(str).str.lower().to_list()
        if any('factura' in x or 'concepto' in x or 'valor' in x or 'pago' in x for x in row_str):
            df_raw.columns = df_raw.iloc[idx]
            df_raw = df_raw.iloc[idx + 1:].reset_index(drop=True)
            break

    # Filtrar filas de totales o vacías
    if not df_raw.empty:
        col_0 = df_raw.columns[0]
        df_raw = df_raw[~df_raw[col_0].astype(str).str.upper().str.contains("TOTAL", na=False)]
    
    # Limpieza estricta de NaN para evitar el error de JSON en Streamlit
    df_raw = df_raw.fillna("").astype(str)
    return df_raw, file_path

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
df_consolidado = pd.concat([df_excel, st.session_state.pagos_nuevos], ignore_index=True).fillna("")

# Detección de columna de valor
col_valor = None
for c in df_consolidado.columns:
    if any(term in str(c).lower() for term in ['valor', 'monto', 'ejecutado', 'pago', 'unnamed: 3']):
        col_valor = c
        break

if col_valor:
    df_consolidado['Valor_Limpio'] = pd.to_numeric(df_consolidado[col_valor].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce').fillna(0)
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
# SECCIÓN 4: TABLA Y DESCARGA EXCEL / CSV
# ----------------------------------------------------
st.subheader("📋 Detalle de Registros")

# Reemplazar valores vacíos para que la tabla no genere SyntaxError
df_mostrar = df_consolidado.drop(columns=['Valor_Limpio'], errors='ignore').astype(str)
st.dataframe(df_mostrar, use_container_width=True)

col_d1, col_d2 = st.columns(2)

# Generar archivo Excel binario
buffer_excel = io.BytesIO()
with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
    df_mostrar.to_excel(writer, index=False, sheet_name='Reporte_Pagos')
data_excel = buffer_excel.getvalue()

with col_d1:
    st.download_button(
        label="📊 Descargar Reporte en Excel (.xlsx)",
        data=data_excel,
        file_name='reporte_consolidado_convenio.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )

with col_d2:
    csv_data = df_mostrar.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Descargar Reporte en CSV (.csv)",
        data=csv_data,
        file_name='reporte_consolidado_convenio.csv',
        mime='text/csv',
    )
