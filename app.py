import streamlit as st
import pandas as pd
import os

# Configuración de pantalla ancha
st.set_page_config(page_title="Seguimiento Convenio 4600017482", page_icon="📱", layout="wide")

st.title("📱 App Seguimiento Financiero - Convenio 4600017482")
st.caption("Transformación Digital Salud Antioquia - Lectura en Vivo del Archivo Excel Local")

EXCEL_FILE = "Seguimiento Financiero Convenio 4600017482 v2.xlsx"

@st.cache_data(ttl=2)
def cargar_datos_excel():
    if not os.path.exists(EXCEL_FILE):
        return None, f"No se encontró el archivo '{EXCEL_FILE}' en la carpeta."
    
    try:
        xls = pd.ExcelFile(EXCEL_FILE)
        
        # Carga estricta únicamente de las páginas indicadas
        df_ejec_convenio = pd.read_excel(xls, sheet_name='Ejecución convenio')
        df_ejec_financiera = pd.read_excel(xls, sheet_name='Ejecución financiera')
        
        return {
            "convenio": df_ejec_convenio,
            "financiera": df_ejec_financiera
        }, None
    except Exception as e:
        return None, str(e)

datos, error = cargar_datos_excel()

if error:
    st.error(f"⚠️ {error}")
    st.info("Por favor, asegúrate de haber copiado el archivo de Excel en la carpeta 'MiAppConvenio'.")
else:
    st.success("✅ Archivo Excel conectado correctamente. Actualización en tiempo real activa.", icon="🔄")
    
    VALOR_TOTAL_CONVENIO = 25982939387
    
    # PASO 1: Selección del Módulo/Página
    st.subheader("PASO 1: Selecciona la Hoja a Consultar")
    modulo = st.radio(
        "Selecciona el reporte:",
        ["1. Ejecución Convenio", "2. Ejecución Financiera"],
        horizontal=True
    )

    # PASO 2: Filtro por Vigencia (Exclusivamente 2025 y 2026)
    vigencia = st.selectbox(
        "Filtrar por Vigencia (Año):",
        ["Todas las Vigencias (2025 - 2026)", "2025", "2026"]
    )

    st.divider()

    if "1. Ejecución Convenio" in modulo:
        st.subheader("PASO 3: Resumen Ejecutivo - Ejecución Convenio")
        
        df_raw = datos["convenio"]
        
        # Extracción y limpieza de estructura
        df_items = df_raw.iloc[7:, [1, 2, 3, 4]].dropna(how='all').copy()
        df_items.columns = ["Fecha / Registro", "Componente", "Soporte / Factura", "Valor Ejecutado ($)"]
        
        df_items["Valor Ejecutado ($)"] = pd.to_numeric(
            df_items["Valor Ejecutado ($)"].astype(str).str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        ).fillna(0)
        
        # Descarte de totales y subtotales
        palabras_clave = "TOTAL|SUBTOTAL|Total|Subtotal|Aportes entregados|Aportes|Saldo"
        df_clean = df_items[
            ~df_items["Fecha / Registro"].astype(str).str.contains(palabras_clave, case=False, na=False) &
            ~df_items["Componente"].astype(str).str.contains(palabras_clave, case=False, na=False)
        ].copy()
        
        # Extracción del año desde la columna de Fecha
        df_clean["Año"] = pd.to_datetime(df_clean["Fecha / Registro"], errors='coerce').dt.year
        
        # Filtro estricto para incluir solo vigencias 2025 y 2026
        df_clean = df_clean[df_clean["Año"].isin([2025, 2026])]
        
        if vigencia != "Todas las Vigencias (2025 - 2026)":
            df_clean = df_clean[df_clean["Año"] == int(vigencia)]

        df_clean["Fecha / Registro"] = df_clean["Fecha / Registro"].astype(str).str.replace(" 00:00:00", "").replace("None", "Sin Fecha")
        
        total_ejecutado = df_clean["Valor Ejecutado ($)"].sum()
        saldo_disponible = VALOR_TOTAL_CONVENIO - total_ejecutado
        pct_ejecucion = (total_ejecutado / VALOR_TOTAL_CONVENIO) * 100 if VALOR_TOTAL_CONVENIO > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Valor Total Convenio", f"${VALOR_TOTAL_CONVENIO:,.0f}")
        col2.metric(f"Total Ejecutado ({vigencia})", f"${total_ejecutado:,.0f}", f"{pct_ejecucion:.1f}%")
        col3.metric("Saldo Disponible", f"${saldo_disponible:,.0f}")

        progreso_val = min(max(pct_ejecucion / 100.0, 0.0), 1.0)
        st.progress(progreso_val, text=f"Porcentaje de Ejecución: {pct_ejecucion:.1f}%")

        st.divider()
        st.subheader("📋 Registros Filtrados (Ejecución Convenio)")
        
        df_display = df_clean[df_clean["Valor Ejecutado ($)"] > 0].drop(columns=["Año"]).copy()
        df_display["Valor Ejecutado ($)"] = df_display["Valor Ejecutado ($)"].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(df_display.astype(str), use_container_width=True)

    else:
        st.subheader("PASO 3: Resumen Ejecutivo - Ejecución Financiera")
        
        df_raw = datos["financiera"]
        
        df_items = df_raw.iloc[8:, [1, 2, 3]].dropna(how='all').copy()
        df_items.columns = ["Fecha", "Valor Ejecutado ($)", "Porcentaje"]
        
        df_items["Valor Ejecutado ($)"] = pd.to_numeric(
            df_items["Valor Ejecutado ($)"].astype(str).str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        ).fillna(0)
        
        palabras_clave = "TOTAL|SUBTOTAL|Total|Subtotal|Aportes entregados|Aportes|Saldo"
        df_clean = df_items[~df_items["Fecha"].astype(str).str.contains(palabras_clave, case=False, na=False)].copy()
        
        df_clean["Año"] = pd.to_datetime(df_clean["Fecha"], errors='coerce').dt.year
        
        # Filtro estricto para vigencias 2025 y 2026
        df_clean = df_clean[df_clean["Año"].isin([2025, 2026])]
        
        if vigencia != "Todas las Vigencias (2025 - 2026)":
            df_clean = df_clean[df_clean["Año"] == int(vigencia)]

        total_ejecutado_fin = df_clean["Valor Ejecutado ($)"].sum()
        pct_fin = (total_ejecutado_fin / VALOR_TOTAL_CONVENIO) * 100 if VALOR_TOTAL_CONVENIO > 0 else 0
        
        col1, col2 = st.columns(2)
        col1.metric(f"Total Ejecutado Financiero ({vigencia})", f"${total_ejecutado_fin:,.0f}")
        col2.metric("Porcentaje sobre Convenio", f"{pct_fin:.2f}%")

        progreso_val_fin = min(max(pct_fin / 100.0, 0.0), 1.0)
        st.progress(progreso_val_fin, text=f"Porcentaje de Ejecución Financiera: {pct_fin:.2f}%")

        st.divider()
        st.subheader("📋 Movimientos (Ejecución Financiera)")
        
        df_display = df_clean[df_clean["Valor Ejecutado ($)"] > 0].drop(columns=["Año"]).copy()
        df_display["Valor Ejecutado ($)"] = df_display["Valor Ejecutado ($)"].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(df_display.astype(str), use_container_width=True)
