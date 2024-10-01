import streamlit as st
import pandas as pd

# Configuración de la aplicación
st.set_page_config(
    page_title="Registro de Sueños",
    page_icon="🔒",
    layout="centered"
)

# ID de Google Sheets
gsheetid = '1OVVjcFBFDOYcbmfqriYmfRke2MexzbjSvbknTwcnatk'  # Reemplaza con tu ID
url = f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid=0'

# Cargar datos
try:
    dfUsuarios = pd.read_csv(url)
    dfUsuarios['celular'] = dfUsuarios['celular'].astype(str).str.replace(',', '')
    dfUsuarios['contrasena'] = dfUsuarios['contrasena'].astype(str).str.replace(',', '')
    dfSueños = pd.read_csv(url)  # Cambia según tu lógica para cargar sueños
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
    nombre_usuario = st.session_state['nombre_usuario']

    # Registro de Sueños
    st.title("Registro de Sueños")
    
    nuevo_sueño = st.text_input("¿Qué sueño deseas alcanzar?")
    respuestas = st.text_area("Respuestas a las preguntas (separa cada respuesta por una línea)")

    if st.button("Registrar Sueño"):
        # Determinar nivel basado en las respuestas
        nivel = calcular_nivel(respuestas)  # Implementa tu lógica aquí

        # Generar objetivos utilizando la IA
        objetivos = generar_objetivos(nuevo_sueño, nivel)  # Implementa la llamada a la IA aquí

        # Guardar en Google Sheets
        guardar_en_sheets(nombre_usuario, nuevo_sueño, nivel, respuestas, objetivos)  # Implementa esta función

        st.success("Sueño registrado correctamente!")

    # Mostrar los sueños existentes
    st.subheader("Tus Sueños")
    sueños_usuario = dfSueños[dfSueños['Nombre'] == nombre_usuario]
    for index, row in sueños_usuario.iterrows():
        st.write(f"Sueño: {row['Sueño']} - Nivel: {row['Nivel']}")
        objetivos_lista = row['Objetivos'].split('\n') if pd.notna(row['Objetivos']) else []
        for objetivo in objetivos_lista:
            if st.checkbox(objetivo):
                # Al marcar el objetivo, actualizar la lista en Google Sheets
                actualizar_objetivos(row['Nombre'], row['sueños'], objetivo)  # Implementa esta función

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
                # Mostrar el registro de sueños directamente
                st.experimental_rerun()  # O puedes omitirlo y permitir que el flujo continúe
            else:
                st.error("Contraseña incorrecta", icon="❌")
        else:
            st.error("Número de celular no encontrado", icon="❌")

    st.markdown("</div>", unsafe_allow_html=True)

# Funciones a implementar
def calcular_nivel(respuestas):
    # Lógica para determinar el nivel basado en respuestas
    return 1  # Cambia esto según tu lógica

def generar_objetivos(sueño, nivel):
    # Lógica para generar objetivos utilizando IA
    return "Objetivo 1\nObjetivo 2\nObjetivo 3"  # Cambia esto según tu lógica

def guardar_en_sheets(nombre, sueño, nivel, respuestas, objetivos):
    # Lógica para guardar en Google Sheets
    pass

def actualizar_objetivos(nombre, sueño, objetivo):
    # Lógica para actualizar los objetivos en Google Sheets
    pass
