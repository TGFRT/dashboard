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
gsheetid = '1OVVjcFBFDOYcbmfqriYmfRke2MexzbjSvbknTwcnatk'

# URL para la hoja
url = f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid=0'

# Cargar datos
try:
    dfUsuarios = pd.read_csv(url)
    st.write("Datos de Registros de Usuarios:")
    st.dataframe(dfUsuarios)  # Mostrar los datos en una tabla
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

# Función para graficar datos (puedes ajustar según tus necesidades)
def cargarGraficos():
    if 'column1' in dfUsuarios.columns and 'column2' in dfUsuarios.columns:  # Ajusta los nombres de las columnas
        fig = px.bar(dfUsuarios, x='column1', y='column2', title="Ejemplo de Gráfico")
        st.plotly_chart(fig, use_container_width=True)

# Llama a la función para cargar gráficos
cargarGraficos()
