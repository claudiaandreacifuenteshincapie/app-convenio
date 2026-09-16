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
        df_cas = pd.read_excel(xls, sheet_name='Ejecución financiera CAS')
        df_crue = pd.read_excel(xls, sheet_name='% Ejecución financiera CRUE')
        df_banco = pd.read_excel(xls, sheet_name='Avance Financiero')
        
        return {
            "cas": df_cas,
            "crue": df_crue,
            "banco": df_banco
        }, None
    except Exception as e:
        return None, str(e)

datos, error = cargar_datos_excel()

if error:
    st.error(f"⚠️ {error}")
    st.info("Por favor, asegúrate de haber copiado el archivo de Excel en la carpeta 'MiAppConvenio'.")
else:
    st.success("✅ Archivo Excel conectado correctamente. Actualización en tiempo real activa.", icon="🔄")
    
    # Valores base del convenio
    VALOR_TOTAL_CAS = 25982939387
    VALOR_TOTAL_CRUE = 1462022598
    
    # PASO 1: Selección del Componente
    st.subheader("PASO 1: Selecciona el Componente a Consultar")
    componente = st.radio(
        "Selecciona el módulo:",
        ["1. Componente CAS (Salud)", "2. Componente CRUE (Otrosí)", "3. Banco IDEA / Rendimientos"],
        horizontal=True
    )

    st.divider()

    if "1. Componente CAS" in componente:
        st.subheader("PASO 2: Resumen Ejecutivo (Componente CAS - Salud)")
        
        df_cas_raw = datos["cas"]
        
        # Filtramos la tabla de facturas de la hoja CAS
        cas_items = df_cas_raw.iloc[7:, [1, 2, 3, 4]].dropna(how='all')
        cas_items.columns = ["Componente", "Fecha", "Soporte / Factura", "Valor Ejecutado ($)"]
        cas_items["Valor Ejecutado ($)"] = pd.to_numeric(cas_items["Valor Ejecutado ($)"], errors='coerce').fillna(0)
        
        total_ejecutado_cas = cas_items["Valor Ejecutado ($)"].sum()
        saldo_cas = VALOR_TOTAL_CAS - total_ejecutado_cas
        pct_cas = (total_ejecutado_cas / VALOR_TOTAL_CAS) * 100 if VALOR_TOTAL_CAS > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Valor Total Convenio", f"${VALOR_TOTAL_CAS:,.0f}")
        col2.metric("Total Ejecutado", f"${total_ejecutado_cas:,.0f}", f"{pct_cas:.1f}%")
        col3.metric("Saldo Disponible", f"${saldo_cas:,.0f}")

        st.progress(pct_cas / 100, text=f"Porcentaje de Ejecución CAS: {pct_cas:.1f}%")

        st.divider()
        st.subheader("📋 Registro Histórico de Pagos (Leído desde Excel)")
        
        cas_items_display = cas_items[cas_items["Valor Ejecutado ($)"] > 0].copy()
        cas_items_display["Valor Ejecutado ($)"] = cas_items_display["Valor Ejecutado ($)"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(cas_items_display, use_container_width=True)

    elif "2. Componente CRUE" in componente:
        st.subheader("PASO 2: Resumen Ejecutivo (Componente CRUE - Otrosí)")
        
        df_crue_raw = datos["crue"]
        crue_items = df_crue_raw.iloc[8:, [1, 2, 3]].dropna(how='all')
        crue_items.columns = ["Fecha", "Valor Ejecutado ($)", "Porcentaje"]
        crue_items["Valor Ejecutado ($)"] = pd.to_numeric(crue_items["Valor Ejecutado ($)"], errors='coerce').fillna(0)
        
        total_ejecutado_crue = crue_items["Valor Ejecutado ($)"].sum()
        saldo_crue = VALOR_TOTAL_CRUE - total_ejecutado_crue
        pct_crue = (total_ejecutado_crue / VALOR_TOTAL_CRUE) * 100 if VALOR_TOTAL_CRUE > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Valor Total CRUE", f"${VALOR_TOTAL_CRUE:,.0f}")
        col2.metric("Total Ejecutado", f"${total_ejecutado_crue:,.0f}", f"{pct_crue:.1f}%")
        col3.metric("Saldo Disponible", f"${saldo_crue:,.0f}")

        st.progress(pct_crue / 100, text=f"Porcentaje de Ejecución CRUE: {pct_crue:.1f}%")

        st.divider()
        st.subheader("📋 Movimientos del Componente CRUE")
        crue_display = crue_items[crue_items["Valor Ejecutado ($)"] > 0].copy()
        crue_display["Valor Ejecutado ($)"] = crue_display["Valor Ejecutado ($)"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(crue_display, use_container_width=True)

    else:
        st.subheader("PASO 2: Estado de Cuenta y Rendimientos (Banco IDEA)")
        
        df_banco_raw = datos["banco"]
        banco_clean = df_banco_raw.iloc[2:, [0, 1, 2, 3, 4, 6, 9]].dropna(how='all')
        banco_clean.columns = ["Cuenta", "Fecha", "Depósitos (+)", "Saldo Inicial", "Rendimientos (+)", "Ejecución (-)", "Saldo Final"]
        
        st.dataframe(banco_clean, use_container_width=True)
