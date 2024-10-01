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
url = f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid=0'

# Cargar datos
try:
    dfUsuarios = pd.read_csv(url)
    dfUsuarios['celular'] = dfUsuarios['celular'].astype(str).str.replace(',', '')
    dfUsuarios['contrasena'] = dfUsuarios['contrasena'].astype(str).str.replace(',', '')
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

# Estilos CSS para mejorar el diseño
st.markdown("""
<style>
    body {
        background-color: #f0f2f5;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        margin: 0;
    }
    .login-form {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
        width: 300px;
        background: white;
        border-radius: 10px;
    }
    .login-form h2 {
        margin-bottom: 20px;
        color: #ff9800;
        text-align: left;
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
        transition: background-color 0.3s;
    }
    .login-form button:hover {
        background-color: #fb8c00;
    }
</style>
""", unsafe_allow_html=True)

# Verificar si el usuario ya ha iniciado sesión
if 'nombre_usuario' in st.session_state:
    st.success(f"Hola {st.session_state['nombre_usuario']} tus datos fueron cargados correctamente", icon="✅")
else:
    # Sección de inicio de sesión
    st.markdown("<div class='login-form'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: left;'>Iniciar Sesión ⭐</h2>", unsafe_allow_html=True)

    celular = st.text_input("Número de Celular:")
    contrasena = st.text_input("Contraseña:", type="password")

    # Verificar si el celular y la contraseña son correctos
    if st.button("Iniciar Sesión"):
        celular_input = celular.replace(',', '')
        if celular_input in dfUsuarios['celular'].values:
            fila = dfUsuarios[dfUsuarios['celular'] == celular_input]
            if fila['contrasena'].values[0] == contrasena:
                # Guardar datos en la sesión
                st.session_state['nombre_usuario'] = fila['nombre'].values[0]
                # Limpiar el formulario
                st.session_state['form_visible'] = False
                # Mostrar solo el mensaje
                st.experimental_set_query_params()
            else:
                st.error("Contraseña incorrecta", icon="❌")
        else:
            st.error("Número de celular no encontrado", icon="❌")

    st.markdown("</div>", unsafe_allow_html=True)
