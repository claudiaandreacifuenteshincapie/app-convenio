import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Seguimiento Financiero - Convenio 4600017482",
    page_icon="📊",
    layout="wide"
)

# Estilos personalizados para mantener elegancia y claridad
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 25px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #2a5298;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar para configuración y selección de vigencia
st.sidebar.image("https://img.icons8.com/color/96/combo-chart--v1.png", width=80)
st.sidebar.markdown("## Configuración y Carga")
vigencia = st.sidebar.selectbox("Selecciona la Vigencia:", [2026, 2025])

st.sidebar.markdown("---")
st.sidebar.markdown("### Base de Datos Excel / CSV")
archivo_subido = st.sidebar.file_uploader("Sube tu archivo base (.xlsx o .csv):", type=["xlsx", "csv"])

# Valores Oficiales Validados por Vigencia
DATOS_OFICIALES_POR_VIGENCIA = {
    2026: {
        "1. Componente CAS (Salud)": {
            "presupuesto": 25982939387.00,
            "ejecutado_base": 14551827858.00,
        },
        "2. Componente CRUE (Otrosí)": {
            "presupuesto": 1462022598.00,
            "ejecutado_base": 384656511.00,
        },
        "3. Consolidado General Convenio": {
            "presupuesto": 27444961985.00,
            "ejecutado_base": 14936484369.00,
        }
    },
    2025: {
        "1. Componente CAS (Salud)": {
            "presupuesto": 20000000000.00,  # Ajusta aquí los valores reales de 2025 si difieren
            "ejecutado_base": 18000000000.00,
        },
        "2. Componente CRUE (Otrosí)": {
            "presupuesto": 1200000000.00,
            "ejecutado_base": 1100000000.00,
        },
        "3. Consolidado General Convenio": {
            "presupuesto": 21200000000.00,
            "ejecutado_base": 19100000000.00,
        }
    }
}

DATOS_OFICIALES = DATOS_OFICIALES_POR_VIGENCIA[vigencia]

# Cabecera principal
st.markdown(f"""
    <div class="main-header">
        <h1>📊 Seguimiento Financiero - Convenio 4600017482</h1>
        <p style="margin: 0; font-size: 1.1em;">Vigencia Seleccionada: <b>{vigencia}</b> | Control Integrado de Pagos y Ejecución</p>
    </div>
""", unsafe_allow_html=True)

# Selección de módulo
modulo = st.radio(
    "Selecciona el componente a consultar:",
    ["1. Componente CAS (Salud)", "2. Componente CRUE (Otrosí)", "3. Consolidado General Convenio"],
    horizontal=True
)

# Inicializar datos en la sesión si no existen
if "df_movimientos_dinamico" not in st.session_state:
    if archivo_subido is not None:
        try:
            if archivo_subido.name.endswith('.csv'):
                df_base = pd.read_csv(archivo_subido)
            else:
                df_base = pd.read_excel(archivo_subido)
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            df_base = None
    else:
        # Datos de prueba iniciales distribuidos por vigencia
        data_ejemplo = [
            {"Vigencia": 2026, "Componente": "1. Componente CAS (Salud)", "Factura": "Pago No. 01", "Fecha": "2026-01-15", "Concepto": "Anticipo CAS 2026", "Valor": 5000000000.00},
            {"Vigencia": 2026, "Componente": "1. Componente CAS (Salud)", "Factura": "Pago No. 12", "Fecha": "2026-03-20", "Concepto": "Ejecución Marzo CAS", "Valor": 9551827858.00},
            {"Vigencia": 2026, "Componente": "2. Componente CRUE (Otrosí)", "Factura": "Pago CRUE 01", "Fecha": "2026-02-10", "Concepto": "Anticipo CRUE 2026", "Valor": 384656511.00},
            {"Vigencia": 2025, "Componente": "1. Componente CAS (Salud)", "Factura": "Pago Histórico 25", "Fecha": "2025-11-10", "Concepto": "Cierre Vigencia 2025 CAS", "Valor": 18000000000.00},
            {"Vigencia": 2025, "Componente": "2. Componente CRUE (Otrosí)", "Factura": "Pago Histórico CRUE", "Fecha": "2025-12-05", "Concepto": "Cierre Vigencia 2025 CRUE", "Valor": 1100000000.00},
        ]
        df_base = pd.DataFrame(data_ejemplo)
    
    if df_base is not None and "Fecha" in df_base.columns:
        df_base["Fecha_dt"] = pd.to_datetime(df_base["Fecha"], errors='coerce')
        df_base["Vigencia"] = df_base["Fecha_dt"].dt.year.fillna(df_base["Vigencia"]).astype(int)
        df_base = df_base.drop(columns=["Fecha_dt"])
    
    st.session_state.df_movimientos_dinamico = df_base

df_movimientos = st.session_state.df_movimientos_dinamico
# Filtrado estricto por la vigencia seleccionada en el selector lateral
df_vigencia = df_movimientos[df_movimientos["Vigencia"] == vigencia] if df_movimientos is not None else pd.DataFrame()

# Cálculo dinámico del ejecutado para la vigencia actual
if modulo == "3. Consolidado General Convenio":
    cas_ejec = df_vigencia[df_vigencia["Componente"] == "1. Componente CAS (Salud)"]["Valor"].sum() if not df_vigencia.empty else 0.0
    crue_ejec = df_vigencia[df_vigencia["Componente"] == "2. Componente CRUE (Otrosí)"]["Valor"].sum() if not df_vigencia.empty else 0.0
    
    if cas_ejec == 0 and crue_ejec == 0:
        ejecutado_act = DATOS_OFICIALES["3. Consolidado General Convenio"]["ejecutado_base"]
    else:
        ejecutado_act = cas_ejec + crue_ejec
else:
    df_mod = df_vigencia[df_vigencia["Componente"] == modulo] if not df_vigencia.empty else pd.DataFrame()
    ejecutado_dinamico = df_mod["Valor"].sum() if not df_mod.empty else 0.0
    ejecutado_base = DATOS_OFICIALES[modulo]["ejecutado_base"]
    ejecutado_act = ejecutado_base if ejecutado_dinamico == 0 else ejecutado_dinamico

presupuesto_act = DATOS_OFICIALES[modulo]["presupuesto"]
saldo_act = presupuesto_act - ejecutado_act
porcentaje_ejec = (ejecutado_act / presupuesto_act) * 100 if presupuesto_act > 0 else 0

# Visualización de Métricas Clave
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=f"PRESUPUESTO ASIGNADO ({vigencia})",
        value=f"${presupuesto_act:,.2f}"
    )

with col2:
    st.metric(
        label=f"TOTAL EJECUTADO ({porcentaje_ejec:.1f}%)",
        value=f"${ejecutado_act:,.2f}"
    )

with col3:
    st.metric(
        label="SALDO DISPONIBLE (SIN EJECUTAR)",
        value=f"${saldo_act:,.2f}"
    )

# Barra de progreso
st.markdown(f"**Progreso de Ejecución General - {modulo} (Vigencia {vigencia}): {porcentaje_ejec:.1f}%**")
st.progress(min(porcentaje_ejec / 100.0, 1.0))

st.markdown("---")

# Pestañas de detalle incluyendo el Universo Completo de Totales filtrado por vigencia
tab1, tab2, tab3 = st.tabs(["📁 Histórico y Detalle", "➕ Registrar Nuevo Pago", f"📊 Universo Completo / Resumen {vigencia}"])

with tab1:
    st.markdown(f"### Detalle de Movimientos - {modulo} (Vigencia {vigencia})")
    
    if not df_vigencia.empty:
        if modulo != "3. Consolidado General Convenio":
            df_filtrado = df_vigencia[df_vigencia["Componente"] == modulo].copy()
        else:
            df_filtrado = df_vigencia.copy()

        if "Valor" in df_filtrado.columns:
            df_filtrado["Valor Formateado"] = df_filtrado["Valor"].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00")

        st.dataframe(df_filtrado, use_container_width=True)

        csv_export = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 Descargar Datos {vigencia} en CSV",
            data=csv_export,
            file_name=f"seguimiento_{vigencia}.csv",
            mime="text/csv"
        )
    else:
        st.info(f"No hay registros específicos para la vigencia {vigencia}. Se muestran los saldos oficiales generales configurados.")

with tab2:
    st.markdown("### Registrar Nuevo Movimiento / Pago")
    with st.form("form_nuevo_pago"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            f_comp = st.selectbox("Componente", ["1. Componente CAS (Salud)", "2. Componente CRUE (Otrosí)"])
            f_factura = st.text_input("Número de Factura / Comprobante")
        with col_f2:
            f_fecha = st.date_input("Fecha del Pago")
            f_valor = st.number_input("Valor del Pago ($)", min_value=0.0, step=1000.0)
        
        f_concepto = st.text_area("Concepto o Descripción")
        submitted = st.form_submit_button("Guardar Registro")
        
        if submitted:
            nueva_vigencia = pd.to_datetime(f_fecha).year
            nuevo_registro = {
                "Vigencia": nueva_vigencia,
                "Componente": f_comp,
                "Factura": f_factura,
                "Fecha": str(f_fecha),
                "Concepto": f_concepto,
                "Valor": f_valor
            }
            
            nuevo_df = pd.DataFrame([nuevo_registro])
            st.session_state.df_movimientos_dinamico = pd.concat(
                [st.session_state.df_movimientos_dinamico, nuevo_df], 
                ignore_index=True
            )
            
            st.success(f"¡Movimiento registrado con éxito para el año {nueva_vigencia}!")
            st.rerun()

with tab3:
    st.markdown(f"### 🌐 Universo Completo del Convenio 4600017482 - Vigencia {vigencia}")
    st.markdown("Tabla consolidada oficial con el desglose de componentes, presupuestos, ejecuciones y saldos para el año seleccionado.")
    
    tabla_universo = [
        {
            "Concepto": "Total Componente CRUE",
            "Presupuesto": DATOS_OFICIALES["2. Componente CRUE (Otrosí)"]["presupuesto"],
            "Ejecutado": DATOS_OFICIALES["2. Componente CRUE (Otrosí)"]["ejecutado_base"],
            "Sin Ejecutar": DATOS_OFICIALES["2. Componente CRUE (Otrosí)"]["presupuesto"] - DATOS_OFICIALES["2. Componente CRUE (Otrosí)"]["ejecutado_base"]
        },
        {
            "Concepto": "Total Componente CAS",
            "Presupuesto": DATOS_OFICIALES["1. Componente CAS (Salud)"]["presupuesto"],
            "Ejecutado": DATOS_OFICIALES["1. Componente CAS (Salud)"]["ejecutado_base"],
            "Sin Ejecutar": DATOS_OFICIALES["1. Componente CAS (Salud)"]["presupuesto"] - DATOS_OFICIALES["1. Componente CAS (Salud)"]["ejecutado_base"]
        },
        {
            "Concepto": "Consolidado General",
            "Presupuesto": DATOS_OFICIALES["3. Consolidado General Convenio"]["presupuesto"],
            "Ejecutado": DATOS_OFICIALES["3. Consolidado General Convenio"]["ejecutado_base"],
            "Sin Ejecutar": DATOS_OFICIALES["3. Consolidado General Convenio"]["presupuesto"] - DATOS_OFICIALES["3. Consolidado General Convenio"]["ejecutado_base"]
        }
    ]
    
    df_universo = pd.DataFrame(tabla_universo)
    
    df_universo_fmt = df_universo.copy()
    for col in ["Presupuesto", "Ejecutado", "Sin Ejecutar"]:
        df_universo_fmt[col] = df_universo_fmt[col].apply(lambda x: f"${x:,.2f}")
        
    st.dataframe(df_universo_fmt, use_container_width=True)
    
    csv_univ = df_universo.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Descargar Universo {vigencia} en CSV",
        data=csv_univ,
        file_name=f"universo_completo_convenio_{vigencia}.csv",
        mime="text/csv"
    )
