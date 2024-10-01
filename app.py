import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la aplicación
st.set_page_config(
    page_title="Demo carga datos desde Google Sheets",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ID de Google Sheets
gsheetid = '1SHgetxf8JaTkgHFKhz78qX6V2Y6LXrRTVBIsFYL9xjE'

# URLs para las hojas
urls = {
    'ventas': f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid=0',
    'categorias': f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid=117226359',
    'mes': f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid=1884410336'
}

# Cargar datos
try:
    dfVentas = pd.read_csv(urls['ventas'])
    dfCategorias = pd.read_csv(urls['categorias'])
    dfMes = pd.read_csv(urls['mes'], usecols=[0, 1])
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

# Funciones para cargar gráficos
def cargarVentasCategoria():
    dfGrupo = dfCategorias.groupby('categoria')['ventas'].sum().reset_index()
    fig = px.bar(dfGrupo, x='categoria', y='ventas', title="Ventas por Categoría")
    st.plotly_chart(fig, use_container_width=True)

def cargarVentasMes():
    fig = px.bar(dfMes, x='categoria', y='sum Total', title="Ventas por Mes")
    st.plotly_chart(fig, use_container_width=True)

# Diseño de columnas
c1, c2 = st.columns(2)
with c1:
    cargarVentasCategoria()
with c2:
    cargarVentasMes()
