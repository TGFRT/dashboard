import streamlit as st
import pandas as pd

# Configuración de la aplicación
st.set_page_config(
    page_title="Inicio de Sesión",
    page_icon="🔒",
    layout="centered"
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

except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

# Estilos CSS para mejorar el diseño
st.markdown("""
<style>
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        background-color: #f0f2f5;
    }
    .login-form {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        width: 300px;
        text-align: center;
    }
    .login-form h2 {
        margin-bottom: 20px;
        color: #333;
    }
    .login-form input {
        width: 100%;
        padding: 10px;
        margin: 10px 0;
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    .login-form button {
        background-color: #ff9800;
        color: white;
        border: none;
        padding: 10px;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
        font-weight: bold;
    }
    .login-form button:hover {
        background-color: #fb8c00;
    }
</style>
""", unsafe_allow_html=True)

# Sección de inicio de sesión
st.markdown('<div class="login-container">', unsafe_allow_html=True)
st.markdown('<div class="login-form">', unsafe_allow_html=True)
st.markdown("<h2>Iniciar Sesión</h2>", unsafe_allow_html=True)

celular = st.text_input("Número de Celular:")
contrasena = st.text_input("Contraseña:", type="password")

# Verificar si el celular y la contraseña son correctos
if st.button("Iniciar Sesión"):
    celular_input = celular.replace(',', '')
    if celular_input in dfUsuarios['celular'].values:
        fila = dfUsuarios[dfUsuarios['celular'] == celular_input]
        if fila['contrasena'].values[0] == contrasena:
            nombre_usuario = fila['nombre'].values[0]
            st.success(f"Inicio de sesión exitoso. Bienvenido, {nombre_usuario}!")
        else:
            st.error("Contraseña incorrecta.")
    else:
        st.error("Número de celular no encontrado.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
