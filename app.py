import streamlit as st
import pandas as pd
import os

# Configuración de página y tema amplio
st.set_page_config(
    page_title="Seguimiento Convenio 4600017482", 
    page_icon="📊", 
    layout="wide"
)

# Estilo personalizado para mejorar la interfaz visual
st.markdown("""
    <style>
    .main-header {
        font-size:2.2rem;
        font-weight:700;
        color:#1E3A8A;
        margin-bottom:0.2rem;
    }
    .sub-header {
        font-size:1.1rem;
        color:#4B5563;
        margin-bottom:1.5rem;
    }
    .stMetric {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 Dashboard de Seguimiento Financiero</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Convenio 4600017482 - Transformación Digital Salud Antioquia</div>', unsafe_allow_html=True)

# Archivo v3 actualizado
EXCEL_FILE = "Seguimiento Financiero Convenio 4600017482 v3.xlsx"

@st.cache_data(ttl=2)
def cargar_datos_excel():
    if not os.path.exists(EXCEL_FILE):
        return None, f"No se encontró el archivo '{EXCEL_FILE}' en la carpeta."
    
    try:
        xls = pd.ExcelFile(EXCEL_FILE)
        
        # Carga estricta de las hojas solicitadas
        df_convenio = pd.read_excel(xls, sheet_name='EJecucion convenio 46000017482')
        df_cas = pd.read_excel(xls, sheet_name='Ejecución financiera CAS')
        
        return {
            "convenio": df_convenio,
            "cas": df_cas
        }, None
    except Exception as e:
        return None, str(e)

datos, error = cargar_datos_excel()

if error:
    st.error(f"⚠️ {error}")
    st.info(f"Asegúrate de que el archivo '{EXCEL_FILE}' esté ubicado correctamente dentro de la carpeta 'MiAppConvenio'.")
else:
    st.sidebar.header("⚙️ Panel de Control")
    st.sidebar.success("✅ Base de Datos v3 Conectada", icon="🔄")
    
    VALOR_TOTAL_CONVENIO = 25982939387

    # Selección de módulo
    modulo = st.sidebar.radio(
        "Selecciona la Métrica/Hoja:",
        ["1. Ejecución Convenio", "2. Ejecución Financiera CAS"]
    )

    # Filtro de vigencias (2025 y 2026)
    vigencia = st.sidebar.selectbox(
        "Filtrar por Vigencia:",
        ["Todas las Vigencias (2025 - 2026)", "2025", "2026"]
    )

    st.sidebar.divider()
    st.sidebar.caption("Sistema de Monitoreo Financiero")

    if "1. Ejecución Convenio" in modulo:
        st.subheader("📋 Módulo: EJecucion convenio 46000017482")
        
        df_raw = datos["convenio"]
        df_items = df_raw.iloc[7:, [1, 2, 3, 4]].dropna(how='all').copy()
        df_items.columns = ["Fecha / Registro", "Componente", "Soporte / Factura", "Valor Ejecutado ($)"]
        
        df_items["Valor Ejecutado ($)"] = pd.to_numeric(
            df_items["Valor Ejecutado ($)"].astype(str).str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        ).fillna(0)
        
        palabras_clave = "TOTAL|SUBTOTAL|Total|Subtotal|Aportes entregados|Aportes|Saldo"
        df_clean = df_items[
            ~df_items["Fecha / Registro"].astype(str).str.contains(palabras_clave, case=False, na=False) &
            ~df_items["Componente"].astype(str).str.contains(palabras_clave, case=False, na=False)
        ].copy()
        
        df_clean["Año"] = pd.to_datetime(df_clean["Fecha / Registro"], errors='coerce').dt.year
        df_clean = df_clean[df_clean["Año"].isin([2025, 2026])]
        
        if vigencia != "Todas las Vigencias (2025 - 2026)":
            df_clean = df_clean[df_clean["Año"] == int(vigencia)]

        df_clean["Fecha / Registro"] = df_clean["Fecha / Registro"].astype(str).str.replace(" 00:00:00", "").replace("None", "Sin Fecha")
        
        total_ejecutado = df_clean["Valor Ejecutado ($)"].sum()
        saldo_disponible = VALOR_TOTAL_CONVENIO - total_ejecutado
        pct_ejecucion = (total_ejecutado / VALOR_TOTAL_CONVENIO) * 100 if VALOR_TOTAL_CONVENIO > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Presupuesto Total Convenio", f"${VALOR_TOTAL_CONVENIO:,.0f}")
        col2.metric(f"Ejecutado ({vigencia})", f"${total_ejecutado:,.0f}", f"{pct_ejecucion:.1f}%")
        col3.metric("Saldo Disponible", f"${saldo_disponible:,.0f}")

        st.markdown("### Avance Financiero Presupuestal")
        progreso_val = min(max(pct_ejecucion / 100.0, 0.0), 1.0)
        st.progress(progreso_val, text=f"Porcentaje Ejecutado: {pct_ejecucion:.2f}%")

        st.divider()
        st.markdown("### 📑 Detalle de Registros y Movimientos")
        
        df_display = df_clean[df_clean["Valor Ejecutado ($)"] > 0].drop(columns=["Año"]).copy()
        df_display["Valor Ejecutado ($)"] = df_display["Valor Ejecutado ($)"].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(df_display.astype(str), use_container_width=True, hide_index=True)

    else:
        st.subheader("📋 Módulo: Ejecución Financiera CAS")
        
        df_raw = datos["cas"]
        df_items = df_raw.iloc[7:, [1, 2, 3, 4]].dropna(how='all').copy()
        df_items.columns = ["Fecha / Registro", "Componente", "Soporte / Factura", "Valor Ejecutado ($)"]
        
        df_items["Valor Ejecutado ($)"] = pd.to_numeric(
            df_items["Valor Ejecutado ($)"].astype(str).str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        ).fillna(0)
        
        palabras_clave = "TOTAL|SUBTOTAL|Total|Subtotal|Aportes entregados|Aportes|Saldo"
        df_clean = df_items[
            ~df_items["Fecha / Registro"].astype(str).str.contains(palabras_clave, case=False, na=False) &
            ~df_items["Componente"].astype(str).str.contains(palabras_clave, case=False, na=False)
        ].copy()
        
        df_clean["Año"] = pd.to_datetime(df_clean["Fecha / Registro"], errors='coerce').dt.year
        df_clean = df_clean[df_clean["Año"].isin([2025, 2026])]
        
        if vigencia != "Todas las Vigencias (2025 - 2026)":
            df_clean = df_clean[df_clean["Año"] == int(vigencia)]

        df_clean["Fecha / Registro"] = df_clean["Fecha / Registro"].astype(str).str.replace(" 00:00:00", "").replace("None", "Sin Fecha")

        total_ejecutado_cas = df_clean["Valor Ejecutado ($)"].sum()
        pct_cas = (total_ejecutado_cas / VALOR_TOTAL_CONVENIO) * 100 if VALOR_TOTAL_CONVENIO > 0 else 0
        
        col1, col2 = st.columns(2)
        col1.metric(f"Total Ejecutado CAS ({vigencia})", f"${total_ejecutado_cas:,.0f}")
        col2.metric("Impacto sobre Convenio Total", f"{pct_cas:.2f}%")

        st.markdown("### Porcentaje de Cumplimiento CAS")
        progreso_val_cas = min(max(pct_cas / 100.0, 0.0), 1.0)
        st.progress(progreso_val_cas, text=f"Porcentaje Ejecutado CAS: {pct_cas:.2f}%")

        st.divider()
        st.markdown("### 📑 Detalle de Movimientos Financieros CAS")
        
        df_display = df_clean[df_clean["Valor Ejecutado ($)"] > 0].drop(columns=["Año"]).copy()
        df_display["Valor Ejecutado ($)"] = df_display["Valor Ejecutado ($)"].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(df_display.astype(str), use_container_width=True, hide_index=True)
