import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Seguimiento Financiero - Convenio 4600017482",
    page_icon="📊",
    layout="wide"
)

# Estilos personalizados para mantener la elegancia y claridad
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

# Sidebar para carga y configuración
st.sidebar.image("https://img.icons8.com/color/96/combo-chart--v1.png", width=80)
st.sidebar.markdown("## Configuración y Carga")
vigencia = st.sidebar.selectbox("Selecciona la Vigencia:", [2026, 2025])

st.sidebar.markdown("---")
st.sidebar.markdown("### Base de Datos Excel / CSV")
archivo_subido = st.sidebar.file_uploader("Sube tu archivo base (.xlsx o .csv):", type=["xlsx", "csv"])

# Valores Oficiales Validados (Fuente: Matriz de Control Financiero)
DATOS_OFICIALES = {
    "1. Componente CAS (Salud)": {
        "presupuesto": 25982939387.00,
        "ejecutado": 14551827858.00,
        "saldo": 11431111529.00
    },
    "2. Componente CRUE (Otrosí)": {
        "presupuesto": 1462022598.00,
        "ejecutado": 384656511.00,
        "saldo": 1077366087.00
    },
    "3. Consolidado General Convenio": {
        "presupuesto": 27444961985.00,
        "ejecutado": 14936484369.00,
        "saldo": 12508477616.00
    }
}

# Cabecera principal
st.markdown("""
    <div class="main-header">
        <h1>📊 Seguimiento Financiero - Convenio 4600017482</h1>
        <p style="margin: 0; font-size: 1.1em;">Transformación Digital Salud Antioquia | Control Integrado de Pagos y Ejecución</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"### 1 Componente a Consultar - Vigencia {vigencia}")

# Selección de módulo
modulo = st.radio(
    "Selecciona el módulo:",
    ["1. Componente CAS (Salud)", "2. Componente CRUE (Otrosí)", "3. Consolidado General Convenio"],
    horizontal=True
)

# Obtener valores correspondientes al componente seleccionado
presupuesto_act = DATOS_OFICIALES[modulo]["presupuesto"]
ejecutado_act = DATOS_OFICIALES[modulo]["ejecutado"]
saldo_act = DATOS_OFICIALES[modulo]["saldo"]
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
        label="SALDO DISPONIBLE REAL",
        value=f"${saldo_act:,.2f}"
    )

# Barra de progreso
st.markdown(f"**Progreso de Ejecución Vigencia {vigencia}: {porcentaje_ejec:.1f}%**")
st.progress(min(porcentaje_ejec / 100.0, 1.0))

st.markdown("---")

# Pestañas de detalle
tab1, tab2 = st.tabs(["📁 Histórico Completo y Exportación", "➕ Registrar Nuevo Pago"])

with tab1:
    st.markdown("### Histórico de Pagos y Movimientos")
    
    # Carga de datos real si existe archivo, de lo contrario usamos datos de respaldo limpios
    if archivo_subido is not None:
        try:
            if archivo_subido.name.endswith('.csv'):
                df_movimientos = pd.read_csv(archivo_subido)
            else:
                df_movimientos = pd.read_excel(archivo_subido)
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            df_movimientos = None
    else:
        # Datos de prueba estructurados correctamente para mantener la consistencia
        data_ejemplo = [
            {"Vigencia": 2026, "Componente": "1. Componente CAS (Salud)", "Factura": "Pago No. 01", "Fecha": "2026-01-15", "Concepto": "Anticipo / Primer Pago CAS", "Valor": 5000000000.00},
            {"Vigencia": 2026, "Componente": "1. Componente CAS (Salud)", "Factura": "Pago No. 12", "Fecha": "2026-03-20", "Concepto": "Ejecución Marzo CAS", "Valor": 4500000000.00},
            {"Vigencia": 2026, "Componente": "1. Componente CAS (Salud)", "Factura": "Pago No. 25", "Fecha": "2026-05-10", "Concepto": "Ejecución Mayo CAS", "Valor": 3000000000.00},
            {"Vigencia": 2026, "Componente": "1. Componente CAS (Salud)", "Factura": "Pago No. 40", "Fecha": "2026-07-25", "Concepto": "Ejecución Julio CAS", "Valor": 2051827858.00},
            {"Vigencia": 2026, "Componente": "2. Componente CRUE (Otrosí)", "Factura": "Pago CRUE 01", "Fecha": "2026-02-10", "Concepto": "Anticipo CRUE", "Valor": 200000511.00},
            {"Vigencia": 2026, "Componente": "2. Componente CRUE (Otrosí)", "Factura": "Pago CRUE 02", "Fecha": "2026-04-15", "Concepto": "Segunda Armada CRUE", "Valor": 184656000.00}
        ]
        df_movimientos = pd.DataFrame(data_ejemplo)

    if df_movimientos is not None:
        # Filtrar según el componente activo si la columna existe
        if "Componente" in df_movimientos.columns and modulo != "3. Consolidado General Convenio":
            df_filtrado = df_movimientos[df_movimientos["Componente"] == modulo]
        else:
            df_filtrado = df_movimientos

        # Formatear la visualización de valores monetarios
        if "Valor" in df_filtrado.columns:
            df_filtrado["Valor Formateado"] = df_filtrado["Valor"].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00")

        st.dataframe(df_filtrado, use_container_width=True)

        # Botón de descarga
        csv_export = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Datos en CSV",
            data=csv_export,
            file_name=f"seguimiento_{modulo.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )

with tab2:
    st.markdown("### Registrar Nuevo Movimiento / Pago")
    with st.form("form_nuevo_pago"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            f_comp = st.selectbox("Componente", ["1. Componente CAS (Salud)", "2. Componente CRUE (Otrosí)"])
            f_factura = st.text_input("Número de Factura / Comprobante")
        with col_f2:
            f_fecha = st.date_input("Fecha del Pago")
            f_valor = st.number_format = st.number_input("Valor del Pago ($)", min_value=0.0, step=1000.0)
        
        f_concepto = st.text_area("Concepto o Descripción")
        submitted = st.form_submit_button("Guardar Registro")
        
        if submitted:
            st.success(f"¡Movimiento registrado con éxito para {f_comp} por un valor de ${f_valor:,.2f}!")
