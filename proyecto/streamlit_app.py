import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import plotly.express as px

# Cargar los archivos desde Google Drive
datos_historicos = pd.read_excel('proyecto/pronosticos (1).xlsx')
datos_pronosticos = pd.read_excel('proyecto/DatosLimpiosOilWell.xlsx')

# Unir los datos en 'Fecha'
datos_completos = pd.merge(datos_historicos, datos_pronosticos, on="Fecha", how="outer")
datos_completos['Fecha'] = pd.to_datetime(datos_completos['Fecha'])
datos_completos.set_index('Fecha', inplace=True)

# Configuración de página
st.set_page_config(page_title="Dashboard de Producción de Petróleo", layout="wide")

# Título principal
st.title("📊 Dashboard de Producción de Petróleo con Pronósticos ARIMA")

# Indicadores Clave en fila superior para múltiples volúmenes
st.markdown("### 📌 Indicadores Clave")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Producción Promedio (Petróleo)", f"{datos_completos['OilVol'].mean():,.2f}")
col2.metric("Producción Máxima (Petróleo)", f"{datos_completos['OilVol'].max():,.2f}")
col3.metric("Producción Mínima (Petróleo)", f"{datos_completos['OilVol'].min():,.2f}")
col4.metric("Producción Promedio (Gas)", f"{datos_completos['GasVol'].mean():,.2f}")
col5.metric("Producción Promedio (Agua)", f"{datos_completos['WaterVol'].mean():,.2f}")
col6.metric("Horas de Operación Promedio", f"{datos_completos['WorkHours'].mean():,.2f}")

st.markdown("---")  # Separador visual

# Gráfico interactivo con zoom de Producción de Petróleo
st.subheader("🔹 Producción de Petróleo con Pronósticos")
st.line_chart(datos_completos[['OilVol', 'PronosticosOilVol']])

# Gráfico personalizado de Volumen de Petróleo sin Intervalos de Confianza
st.subheader("🔹 Producción de Petróleo con Pronósticos")
fig = go.Figure()
fig.add_trace(go.Scatter(x=datos_completos.index, y=datos_completos['OilVol'], mode='lines', name='Producción Real'))
fig.add_trace(go.Scatter(x=datos_completos.index, y=datos_completos['PronosticosOilVol'], mode='lines', name='Pronóstico ARIMA', line=dict(dash='dash')))
fig.update_layout(title="Producción de Petróleo", xaxis_title="Fecha", yaxis_title="Volumen de Petróleo")
st.plotly_chart(fig, use_container_width=True)

# Gráficos de Agua y Gas
st.subheader("🌊 Producción de Agua")
st.line_chart(datos_completos[['WaterVol', 'PronosticosWaterVol']])

st.subheader("🔹 Producción de Gas")
st.line_chart(datos_completos[['GasVol', 'PronosticosGasVol']])

st.markdown("---")  # Otro separador visual

# Descomposición de la Serie Temporal
st.markdown("### 🔎 Descomposición de la Serie Temporal de Producción de Petróleo")
descomposicion = sm.tsa.seasonal_decompose(datos_completos['OilVol'], model='additive')
fig = go.Figure()
fig.add_trace(go.Scatter(x=datos_completos.index, y=descomposicion.trend, mode='lines', name="Tendencia"))
fig.add_trace(go.Scatter(x=datos_completos.index, y=descomposicion.seasonal, mode='lines', name="Estacionalidad"))
fig.add_trace(go.Scatter(x=datos_completos.index, y=descomposicion.resid, mode='lines', name="Residuos"))
fig.update_layout(title="Descomposición de la Serie Temporal", xaxis_title="Fecha", yaxis_title="Valor")
st.plotly_chart(fig, use_container_width=True)

# Comparativo de Períodos
st.markdown("### 📊 Comparativo de Producción por Año")
datos_por_anio = datos_completos.resample('Y').mean()
fig = px.bar(datos_por_anio, x=datos_por_anio.index.year, y=['OilVol', 'WaterVol', 'GasVol'], title="Comparativo Anual de Producción")
fig.update_layout(xaxis_title="Año", yaxis_title="Volumen Promedio")
st.plotly_chart(fig, use_container_width=True)

# Descripción y contexto
st.markdown("""
    ### 📄 Descripción
    Este dashboard permite visualizar la producción histórica de petróleo, gas y agua, así como los pronósticos obtenidos mediante el modelo ARIMA.
    Cada gráfico compara el volumen real con el pronóstico estimado.
""")

# Guía de variables en la barra lateral
st.sidebar.markdown("### 📘 Guía de Variables")
st.sidebar.markdown("""
1. **OilVol**: m³/día - Volumen de petróleo producido.
2. **VolLiq**: m³/día - Cantidad total de líquido (mezcla de petróleo, gas y agua) producida por el pozo.
3. **GasVol**: m³/día - Cantidad de gas producido por el pozo.
4. **WaterVol**: m³/día - Cantidad de agua extraída.
5. **WaterCut**: % - Proporción de agua en el líquido extraído.
6. **WorkHours**: Horas de operación al día.
7. **DnmcLvl**: m - Altura del fluido en el pozo durante la operación.
8. **Pressure**: atm - Presión del reservorio medida en atmósferas.
""")