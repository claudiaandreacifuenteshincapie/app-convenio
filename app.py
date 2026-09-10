import streamlit as st
import pandas as pd
import os
import io

# Configuración de página amplia
st.set_page_config(
    page_title="Seguimiento Convenio 4600017482", 
    page_icon="📊", 
    layout="wide"
)

# Estilos personalizados para la interfaz
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

def procesar_hoja(df_raw):
    # Hacer una copia limpia
    df = df_raw.dropna(how='all').copy()
    
    # Asignar nombres a las primeras 4 columnas
    cols = df.columns[:4]
    df_sub = df[cols].copy()
    df_sub.columns = ["Fecha / Registro", "Componente", "Soporte / Factura", "Valor Ejecutado ($)"]
    
    # Limpieza de montos financieros
    def limpiar_monto(val):
        val_str = str(val).replace('$', '').replace(',', '').replace('.', '').strip()
        try:
            return float(val_str)
        except:
            return 0.0

    df_sub["Monto_Numerico"] = df_sub["Valor Ejecutado ($)"].apply(limpiar_monto)
    
    # Filtrar filas que son totales, encabezados o vacías
    palabras_basura = ["total", "subtotal", "saldo", "componente", "fecha / registro", "nan", "none"]
    
    def es_fila_valida(row):
        col0 = str(row["Fecha / Registro"]).lower().strip()
        col1 = str(row["Componente"]).lower().strip()
        if any(p in col0 for p in palabras_basura) or any(p in col1 for p in palabras_basura):
            return False
        return True

    df_filtrado = df_sub[df_sub.apply(es_fila_valida, axis=1)].copy()
    
    # Extraer el año
    df_filtrado["Año"] = pd.to_datetime(df_filtrado["Fecha / Registro"], errors='coerce', dayfirst=True).dt.year
    df_filtrado["Año"] = df_filtrado["Año"].fillna(
        df_filtrado["Fecha / Registro"].astype(str).str.extract(r'(202[4-9])')[0]
    )
    
    return df_filtrado

def generar_excel_descarga(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Informe')
    return output.getvalue()

datos, error = cargar_datos_excel()

if error:
    st.error(f"⚠️ {error}")
    st.info(f"Asegúrate de que el archivo '{EXCEL_FILE}' esté subido en GitHub.")
else:
    st.sidebar.header("⚙️ Panel de Control")
    st.sidebar.success("✅ Base de Datos Conectada", icon="🔄")
    
    VALOR_TOTAL_CONVENIO = 25982939387

    modulo = st.sidebar.radio(
        "Selecciona el Módulo:",
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
        hoja_actual = 'EJecucion convenio 46000017482'
    else:
        st.subheader("📋 Módulo: Ejecución Financiera CAS")
        df_clean = procesar_hoja(datos["cas"])
        hoja_actual = 'Ejecución financiera CAS'

    # Aplicar filtro por año
    if vigencia != "Todas las Vigencias (2025 - 2026)":
        df_display_base = df_clean[df_clean["Año"].astype(str).str.contains(str(vigencia), na=False)]
    else:
        df_display_base = df_clean.copy()

    df_display_base["Fecha / Registro"] = (
        df_display_base["Fecha / Registro"]
        .astype(str)
        .str.replace(" 00:00:00", "")
        .str.replace("None", "Sin Fecha")
    )
    
    total_ejecutado = df_display_base["Monto_Numerico"].sum()
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

    # Formulario para registrar nuevos pagos o facturas
    with st.expander("➕ Registrar Nuevo Pago o Factura en Excel"):
        with st.form("form_registro", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            nueva_fecha = col_f1.date_input("Fecha de Registro")
            nuevo_componente = col_f1.text_input("Componente / Descripción")
            nuevo_soporte = col_f2.text_input("N° Soporte / Factura")
            nuevo_valor = col_f2.number_input("Valor Ejecutado ($)", min_value=0.0, step=1000.0)
            
            btn_guardar = st.form_submit_button("💾 Guardar Registro en Excel")
            
            if btn_guardar:
                if nuevo_componente and nuevo_soporte and nuevo_valor > 0:
                    nueva_fila = pd.DataFrame([{
                        "Fecha / Registro": str(nueva_fecha),
                        "Componente": nuevo_componente,
                        "Soporte / Factura": nuevo_soporte,
                        "Valor Ejecutado ($)": nuevo_valor
                    }])
                    
                    try:
                        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                            df_existente = pd.read_excel(EXCEL_FILE, sheet_name=hoja_actual)
                            df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
                            df_actualizado.to_excel(writer, sheet_name=hoja_actual, index=False)
                        
                        st.success("✅ Registro guardado con éxito en el archivo Excel.")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as ex:
                        st.error(f"No se pudo guardar el registro: {ex}")
                else:
                    st.warning("⚠️ Por favor completa todos los campos con información válida.")

    st.markdown("### 📑 Detalle de Registros y Movimientos")
    
    df_tabla = df_display_base[["Fecha / Registro", "Componente", "Soporte / Factura", "Monto_Numerico"]].copy()
    df_tabla.columns = ["Fecha / Registro", "Componente", "Soporte / Factura", "Valor Ejecutado ($)"]
    
    df_export = df_tabla.copy()
    df_tabla["Valor Ejecutado ($)"] = df_tabla["Valor Ejecutado ($)"].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(df_tabla.astype(str), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### 📥 Exportar Informes")
    
    col_exp1, col_exp2 = st.columns(2)
    
    # Exportar a Excel
    excel_data = generar_excel_descarga(df_export)
    col_exp1.download_button(
        label="🟢 Descargar Informe en Excel (.xlsx)",
        data=excel_data,
        file_name=f"Informe_{modulo.replace(' ', '_')}_{vigencia}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Exportar para PDF
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
        {df_tabla.to_html(index=False)}
    </body>
    </html>
    """
    
    col_exp2.download_button(
        label="🔴 Descargar Informe para PDF (.html / Imprimir)",
        data=html_report,
        file_name=f"Informe_{modulo.replace(' ', '_')}_{vigencia}.html",
        mime="text/html"
    )
