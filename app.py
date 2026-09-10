import streamlit as st
import pandas as pd
import os
import io
import re

# Configuración de página
st.set_page_config(
    page_title="Seguimiento Convenio 4600017482", 
    page_icon="📊", 
    layout="wide"
)

# Estilos de interfaz
st.markdown("""
    <style>
    .main-header { font-size:2.2rem; font-weight:700; color:#1E3A8A; margin-bottom:0.2rem; }
    .sub-header { font-size:1.1rem; color:#4B5563; margin-bottom:1.5rem; }
    .stMetric { background-color: #F3F4F6; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
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
        df_convenio = pd.read_excel(xls, sheet_name='EJecucion convenio 46000017482', header=None)
        df_cas = pd.read_excel(xls, sheet_name='Ejecución financiera CAS', header=None)
        
        return {
            "convenio": df_convenio,
            "cas": df_cas
        }, None
    except Exception as e:
        return None, str(e)

def procesar_hoja_alineada(df_raw):
    if df_raw is None or df_raw.empty:
        return pd.DataFrame()

    # Buscar la fila de encabezados reales que contenga palabras clave
    header_idx = None
    for idx, row in df_raw.iterrows():
        row_str = " ".join([str(val).lower() for val in row.values if pd.notna(val)])
        if "fecha" in row_str or "componente" in row_str or "soporte" in row_str or "factura" in row_str or "valor" in row_str:
            header_idx = idx
            break

    if header_idx is not None:
        # Tomar los datos a partir de la fila siguiente al encabezado
        df_data = df_raw.iloc[header_idx + 1:].copy().reset_index(drop=True)
    else:
        df_data = df_raw.copy()

    # Eliminar columnas completamente vacías
    df_data = df_data.dropna(how='all', axis=1)

    registros = []
    
    for _, row in df_data.iterrows():
        vals = [val for val in row.values if pd.notna(val) and str(val).strip() != ""]
        if len(vals) < 2:
            continue
        
        row_str = " ".join([str(v) for v in vals]).lower()
        if "total" in row_str or "subtotal" in row_str or "convenio" in row_str:
            continue

        # Detección inteligente de columnas por tipo de contenido
        fecha, componente, soporte, monto_num, anio = "Sin Fecha", "CAS", "", 0.0, "Sin Año"
        
        for v in vals:
            v_str = str(v).strip()
            # Buscar fecha (dd/mm/yyyy o yyyy-mm-dd)
            if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', v_str) or re.search(r'202[4-9]', v_str):
                if fecha == "Sin Fecha":
                    fecha = v_str.replace(" 00:00:00", "")
                    match_anio = re.search(r'(202[4-9])', v_str)
                    if match_anio:
                        anio = match_anio.group(1)
            # Buscar factura / soporte
            elif re.search(r'factura|soporte|fac|doc|nr|n°', v_str.lower()) or (v_str.isalnum() and not v_str.isdigit() and len(v_str) > 3):
                soporte = v_str
            # Buscar monto numérico elevado
            elif isinstance(v, (int, float)) or (isinstance(v, str) and re.search(r'\d+', v)):
                monto_clean = re.sub(r'[^\d.]', '', v_str.replace('.', '').replace(',', '.'))
                try:
                    num = float(monto_clean)
                    if num > 1000: # Evita tomar el número de ítem/secuencia como valor
                        monto_num = num
                except:
                    pass
            # Texto descriptivo / componente
            elif len(v_str) > 2 and not v_str.replace('.', '').isdigit():
                componente = v_str

        if monto_num > 0 or fecha != "Sin Fecha":
            registros.append({
                "Fecha / Registro": fecha,
                "Componente": componente,
                "Soporte / Factura": soporte if soporte else "S/D",
                "Monto_Numerico": monto_num,
                "Año": anio
            })

    return pd.DataFrame(registros)

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
        df_clean = procesar_hoja_alineada(datos["convenio"])
        hoja_actual = 'EJecucion convenio 46000017482'
    else:
        st.subheader("📋 Módulo: Ejecución Financiera CAS")
        df_clean = procesar_hoja_alineada(datos["cas"])
        hoja_actual = 'Ejecución financiera CAS'

    # Filtrar por año
    if vigencia != "Todas las Vigencias (2025 - 2026)" and not df_clean.empty:
        df_filtrado = df_clean[df_clean["Año"] == str(vigencia)].copy()
        if df_filtrado.empty:
            df_filtrado = df_clean.copy()
    else:
        df_filtrado = df_clean.copy()

    total_ejecutado = df_filtrado["Monto_Numerico"].sum() if not df_filtrado.empty else 0.0
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

    # Formulario
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
    
    if not df_filtrado.empty:
        df_display = df_filtrado[["Fecha / Registro", "Componente", "Soporte / Factura", "Monto_Numerico"]].copy()
        df_display.columns = ["Fecha / Registro", "Componente", "Soporte / Factura", "Valor Ejecutado ($)"]
        
        df_export = df_display.copy()
        df_display["Valor Ejecutado ($)"] = df_display["Valor Ejecutado ($)"].apply(lambda x: f"${x:,.0f}")
        
        st.dataframe(df_display.astype(str), use_container_width=True, hide_index=True)
    else:
        st.warning("No se encontraron registros válidos.")

    st.divider()
    st.markdown("### 📥 Exportar Informes")
    
    col_exp1, col_exp2 = st.columns(2)
    
    if not df_filtrado.empty:
        excel_data = generar_excel_descarga(df_export)
        col_exp1.download_button(
            label="🟢 Descargar Informe en Excel (.xlsx)",
            data=excel_data,
            file_name=f"Informe_{modulo.replace(' ', '_')}_{vigencia}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
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
