import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Financiero - Convenio 4600017482",
    page_icon="📊",
    layout="wide"
)

# Estilos personalizados para una visualización limpia
st.markdown("""
    <style>
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.image("https://img.icons8.com/color/96/data-configuration.png", width=80)
st.sidebar.markdown("### Configuración y Carga")

vigencia_sel = st.sidebar.selectbox("Selecciona la Vigencia:", [2026, 2025, 2027], index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("#### Base de Datos Excel / CSV")
archivo_subido = st.sidebar.file_uploader("Sube tu archivo base (.xlsx o .csv):", type=["xlsx", "csv"])

# Datos iniciales por defecto si no se carga archivo (simulando la realidad del convenio)
@st.cache_data
def cargar_datos_iniciales():
    data = {
        "Vigencia": [2026, 2026, 2026, 2026],
        "Componente": [
            "1. Componente CAS (Salud)",
            "1. Componente CAS (Salud)",
            "1. Componente CAS (Salud)",
            "1. Componente CAS (Salud)"
        ],
        "Factura": ["Pago No. 01", "Pago No. 12", "Pago No. 25", "Pago No. 40"],
        "Fecha": ["2026-01-15", "2026-03-20", "2026-05-10", "2026-07-25"],
        "Concepto": [
            "Anticipo / Primer Pago CAS",
            "Ejecución Marzo CAS",
            "Ejecución Mayo CAS",
            "Ejecución Julio CAS"
        ],
        "Valor": [5000000000.0, 4500000000.0, 3000000000.0, 2405908982.0]
    }
    return pd.DataFrame(data)

# Carga de datos con persistencia en session_state
if "df" not in st.session_state:
    if archivo_subido is not None:
        try:
            if archivo_subido.name.endswith('.csv'):
                st.session_state.df = pd.read_csv(archivo_subido)
            else:
                st.session_state.df = pd.read_excel(archivo_subido)
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            st.session_state.df = cargar_datos_iniciales()
    else:
        st.session_state.df = cargar_datos_iniciales()

df = st.session_state.df

# Asegurar tipos de datos correctos para evitar errores de cálculo
df["Vigencia"] = pd.to_numeric(df["Vigencia"], errors="coerce").fillna(2026).astype(int)
df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0.0)

# Filtrar por vigencia seleccionada
df_vigencia = df[df["Vigencia"] == vigencia_sel]

# Encabezado Principal
st.markdown("""
    <div style='background-color: #1E3A8A; padding: 20px; border-radius: 10px; color: white;'>
        <h2>📊 Seguimiento Financiero - Convenio 4600017482</h2>
        <p>Transformación Digital Salud Antioquia | Control Integrado de Pagos y Ejecución</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"### 1 Componente a Consultar - Vigencia {vigencia_sel}")
modulo_sel = st.radio(
    "Selecciona el módulo:",
    ["1. Componente CAS (Salud)", "2. Componente CRUE (Otrosí)", "3. Consolidado General Convenio"],
    horizontal=True
)

# Filtrar por componente si aplica
if modulo_sel != "3. Consolidado General Convenio":
    df_filtrado = df_vigencia[df_vigencia["Componente"] == modulo_sel]
else:
    df_filtrado = df_vigencia

# Definir Presupuesto Asignado según el componente o vigencia
presupuestos_base = {
    2026: {
        "1. Componente CAS (Salud)": 25982939387.0,
        "2. Componente CRUE (Otrosí)": 5000000000.0,
        "3. Consolidado General Convenio": 30982939387.0
    },
    2025: {
        "1. Componente CAS (Salud)": 20000000000.0,
        "2. Componente CRUE (Otrosí)": 4000000000.0,
        "3. Consolidado General Convenio": 24000000000.0
    },
    2027: {
        "1. Componente CAS (Salud)": 15000000000.0,
        "2. Componente CRUE (Otrosí)": 3000000000.0,
        "3. Consolidado General Convenio": 18000000000.0
    }
}

presupuesto_asignado = presupuestos_base.get(vigencia_sel, {}).get(modulo_sel, 25982939387.0)
total_ejecutado = df_filtrado["Valor"].sum()
saldo_disponible = presupuesto_asignado - total_ejecutado
porcentaje_ejecucion = (total_ejecutado / presupuesto_asignado * 100) if presupuesto_asignado > 0 else 0.0

# Tarjetas de Indicadores Financieros
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=f"PRESUPUESTO ASIGNADO ({vigencia_sel})",
        value=f"${presupuesto_asignado:,.2f}"
    )

with col2:
    st.metric(
        label=f"TOTAL EJECUTADO ({porcentaje_ejecucion:.1f}%)",
        value=f"${total_ejecutado:,.2f}"
    )

with col3:
    st.metric(
        label="SALDO DISPONIBLE REAL",
        value=f"${saldo_disponible:,.2f}"
    )

# Barra de progreso
st.markdown(f"**Progreso de Ejecución Vigencia {vigencia_sel}: {porcentaje_ejecucion:.1f}%**")
st.progress(min(max(porcentaje_ejecucion / 100.0, 0.0), 1.0))

st.markdown("---")

# Pestañas de Interacción
tab_hist, tab_reg = st.tabs(["📁 Histórico Completo y Exportación", "➕ Registrar Nuevo Pago"])

with tab_hist:
    st.markdown("#### Histórico de Pagos y Movimientos")
    if not df_filtrado.empty:
        df_display = df_filtrado.copy()
        df_display["Valor Formateado"] = df_display["Valor"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df_display[["Vigencia", "Componente", "Factura", "Fecha", "Concepto", "Valor Formateado"]], use_container_width=True)
        
        # Botón para descargar CSV actualizado
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Datos en CSV",
            data=csv,
            file_name=f"seguimiento_financiero_{vigencia_sel}.csv",
            mime="text/csv",
        )
    else:
        st.info("No hay registros disponibles para los filtros seleccionados.")

with tab_reg:
    st.markdown("#### Registro de Nuevo Pago o Movimiento Presupuestal")
    with st.form("form_nuevo_pago"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            nueva_vigencia = st.selectbox("Vigencia", [2026, 2025, 2027], index=0)
            nuevo_componente = st.selectbox("Componente", ["1. Componente CAS (Salud)", "2. Componente CRUE (Otrosí)"])
            nueva_factura = st.text_input("Número de Factura / Documento", "Pago No. XX")
        with col_f2:
            nueva_fecha = st.date_input("Fecha del Pago", datetime.now())
            nuevo_concepto = st.text_input("Concepto o Descripción", "Ejecución mensual...")
            nuevo_valor = st.number_input("Valor del Pago ($)", min_value=0.0, step=1000.0, format="%.2f")
            
        submitted = st.form_submit_button("Guardar y Actualizar Cálculos")
        
        if submitted:
            if not nueva_factura or not nuevo_concepto:
                st.warning("Por favor completa todos los campos obligatorios.")
            else:
                nuevo_registro = pd.DataFrame({
                    "Vigencia": [int(nueva_vigencia)],
                    "Componente": [nuevo_componente],
                    "Factura": [nueva_factura],
                    "Fecha": [str(nueva_fecha)],
                    "Concepto": [nuevo_concepto],
                    "Valor": [float(nuevo_valor)]
                })
                # Concatenar el nuevo registro al DataFrame en session_state
                st.session_state.df = pd.concat([st.session_state.df, nuevo_registro], ignore_index=True)
                st.success("¡Registro agregado exitosamente! Las cifras y el saldo disponible se han recalculado en tiempo real.")
                st.rerun()
