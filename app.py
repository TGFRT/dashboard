import streamlit as st
import pandas as pd

# Configuración de la aplicación
st.set_page_config(
    page_title="Registro de Sueños",
    page_icon="🔒",
    layout="centered"
)

# ID de Google Sheets
gsheetid = 'your_gsheet_id'  # Reemplaza con tu ID de Google Sheets
url = f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid=0'

# Cargar datos
try:
    dfSueños = pd.read_csv(url)
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

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
    for index, row in dfSueños[dfSueños['Nombre'] == nombre_usuario].iterrows():
        st.write(f"Sueño: {row['Sueño']} - Nivel: {row['Nivel']}")
        objetivos_lista = row['Objetivos'].split('\n') if pd.notna(row['Objetivos']) else []
        for objetivo in objetivos_lista:
            if st.checkbox(objetivo):
                # Al marcar el objetivo, actualizar la lista en Google Sheets
                actualizar_objetivos(row['Nombre'], row['Sueño'], objetivo)  # Implementa esta función

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
                st.experimental_rerun()  # Recargar la página para mostrar el registro de sueños
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
