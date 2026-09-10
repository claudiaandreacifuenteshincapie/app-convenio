import streamlit as st
import pandas as pd
import os
import io

# Configuración de página y tema amplio
st.set_page_config(
    page_title="Seguimiento Convenio 4600017482", 
    page_icon="📊", 
    layout="wide"
)

# Estilo personalizado para la interfaz visual
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

EXCEL_FILE = "Seguimiento Financiero Convenio 4600017482 v3.xlsx"

@st.cache_data(ttl=2)
def cargar_datos_excel():
    if not os.path.exists(EXCEL_FILE):
        return None, f"No se encontró el archivo '{EXCEL_FILE}' en la carpeta."
    
    try:
        xls = pd.ExcelFile(EXCEL_FILE)
        
        df_convenio = pd.read_excel(xls, sheet_name='EJecucion convenio 46000017482')
        df_cas = pd.read_excel(xls, sheet_name='Ejecución financiera CAS')
        
        return {
            "convenio": df_convenio,
            "cas": df_cas
        }, None
    except Exception as e:
        return None, str(e)

def generar_excel_descarga(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Informe')
    return output.getvalue()

def procesar_hoja(df_raw):
    # Detectar dinámicamente las columnas necesarias sin cortar registros por índices fijos
    df_items = df_raw.dropna(how='all').copy()
    
    # Seleccionar las primeras 4 columnas con datos
    df_items = df_items.iloc[:, :4]
    df_items.columns = ["Fecha / Registro", "Componente", "Soporte / Factura", "Valor Ejecutado ($)"]
    
    # Limpieza estricta de valores numéricos
    df_items["Valor Limpio"] = (
        df_items["Valor Ejecutado ($)"]
        .astype(str)
        .str.replace('$', '', regex=False)
        .str.replace(',', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.strip()
    )
    
    df_items["Valor Ejecutado ($)"] = pd.to_numeric(df_items["Valor Limpio"], errors='coerce').fillna(0)
    
    # Exclusión de filas de resúmenes/totales
    palabras_clave = "TOTAL|SUBTOTAL|Total|Subtotal|Aportes entregados|Aportes|Saldo"
    df_clean = df_items[
        ~df_items["Fecha / Registro"].astype(str).str.contains(palabras_clave, case=False, na=False) &
        ~df_items["Componente"].astype(str).str.contains(palabras_clave, case=False, na=False)
    ].copy()
    
    # Manejo de fechas y extracción de año
    df_clean["Año"] = pd.to_datetime(df_clean["Fecha / Registro"], errors='coerce').dt.year
    
    return df_clean

datos, error = cargar_datos_excel()

if error:
    st.error(f"⚠️ {error}")
    st.info(f"Asegúrate de que el archivo '{EXCEL_FILE}' esté ubicado correctamente dentro de la carpeta 'MiAppConvenio'.")
else:
    st.sidebar.header("⚙️ Panel de Control")
    st.sidebar.success("✅ Base de Datos v3 Conectada", icon="🔄")
    
    VALOR_TOTAL_CONVENIO = 25982939387

    modulo = st.sidebar.radio(
        "Selecciona la Métrica/Hoja:",
        ["1. Ejecución Convenio", "2. Ejecución Financiera CAS"]
    )

    vigencia = st.sidebar.selectbox(
        "Filtrar por Vigencia:",
        ["Todas las Vigencias (2025 - 2026)", "2025", "2026"]
    )

    st.sidebar.divider()
    st.sidebar.caption("Sistema de Monitoreo Financiero")

    if "1. Ejecución Convenio" in modulo:
        st.subheader("📋 Módulo: EJecucion convenio 46000017482")
        df_clean = procesar_hoja(datos["convenio"])
    else:
        st.subheader("📋 Módulo: Ejecución Financiera CAS")
        df_clean = procesar_hoja(datos["cas"])

    # Filtro por vigencia 2025/2026
    df_clean = df_clean[df_clean["Año"].isin([2025, 2026]) | df_clean["Año"].isna()]
    
    if vigencia != "Todas las Vigencias (2025 - 2026)":
        df_clean = df_clean[df_clean["Año"] == int(vigencia)]

    df_clean["Fecha / Registro"] = df_clean["Fecha / Registro"].astype(str).str.replace(" 00:00:00", "").replace("None", "Sin Fecha")
    
    total_ejecutado = df_clean["Valor Ejecutado ($)"].sum()
    saldo_disponible = VALOR_TOTAL_CONVENIO - total_ejecutado
    pct_ejecucion = (total_ejecutado / VALOR_TOTAL_CONVENIO) * 100 if VALOR_TOTAL_CONVENIO > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Presupuesto Total Convenio", f"${VALOR_TOTAL_CONVENIO:,.0f}")
    col2.metric(f"Ejecutado ({vigencia})", f"${total_ejecutado:,.0f}", f"{pct_ejecucion:.2f}%")
    col3.metric("Saldo Disponible", f"${saldo_disponible:,.0f}")

    st.markdown("### Avance Financiero Presupuestal")
    progreso_val = min(max(pct_ejecucion / 100.0, 0.0), 1.0)
    st.progress(progreso_val, text=f"Porcentaje Ejecutado: {pct_ejecucion:.2f}%")

    st.divider()
    st.markdown("### 📑 Detalle de Registros y Movimientos")
    
    df_display = df_clean[df_clean["Valor Ejecutado ($)"] > 0].drop(columns=["Año", "Valor Limpio"], errors="ignore").copy()
    
    # Preparación de datos para la vista
    df_export = df_display.copy()
    df_display["Valor Ejecutado ($)"] = df_display["Valor Ejecutado ($)"].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(df_display.astype(str), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### 📥 Exportar Informes")
    
    col_exp1, col_exp2 = st.columns(2)
    
    # Descarga en Excel
    excel_data = generar_excel_descarga(df_export)
    col_exp1.download_button(
        label="🟢 Descargar Informe en Excel (.xlsx)",
        data=excel_data,
        file_name=f"Informe_{modulo.replace(' ', '_')}_{vigencia}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Descarga en HTML / PDF Imprimible
    html_report = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h2 {{ color: #1E3A8A; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #dddddd; text-align: left; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h2>Reporte Financiero - Convenio 4600017482</h2>
        <p><b>Módulo:</b> {modulo}</p>
        <p><b>Vigencia:</b> {vigencia}</p>
        <p><b>Total Ejecutado:</b> ${total_ejecutado:,.0f}</p>
        <hr>
        {df_display.to_html(index=False)}
    </body>
    </html>
    """
    
    col_exp2.download_button(
        label="🔴 Descargar Informe para PDF (.html / Imprimir)",
        data=html_report,
        file_name=f"Informe_{modulo.replace(' ', '_')}_{vigencia}.html",
        mime="text/html"
    )
