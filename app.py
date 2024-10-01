import streamlit as st
import pandas as pd

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

    # Asegurarse de que la columna 'celular' y 'contrasena' sean de tipo string y eliminar comas
    dfUsuarios['celular'] = dfUsuarios['celular'].astype(str).str.replace(',', '')
    dfUsuarios['contrasena'] = dfUsuarios['contrasena'].astype(str).str.replace(',', '')

    # Imprimir los nombres de las columnas para verificar
    st.write("Columnas disponibles:", dfUsuarios.columns.tolist())
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

# Sección de inicio de sesión
st.header("Iniciar Sesión")
celular = st.text_input("Número de Celular:")
contrasena = st.text_input("Contraseña:", type="password")

# Verificar si el celular y la contraseña son correctos
if st.button("Iniciar Sesión"):
    celular_input = celular.replace(',', '')
    if celular_input in dfUsuarios['celular'].values:
        fila = dfUsuarios[dfUsuarios['celular'] == celular_input]
        if fila['contrasena'].values[0] == contrasena:
            nombre_usuario = fila['nombre'].values[0]  # Ajusta 'Nombre' según el nombre de tu columna
            st.success(f"Inicio de sesión exitoso. Bienvenido, {nombre_usuario}!")
        else:
            st.error("Contraseña incorrecta.")
    else:
        st.error("Número de celular no encontrado.")
