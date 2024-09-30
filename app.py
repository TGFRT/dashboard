import streamlit as st
import google.generativeai as gen_ai
from difflib import SequenceMatcher
import re

# Función para calcular la similitud entre dos textos
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Función para normalizar el texto
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'(.)\1+', r'\1', text)
    return text

# Configura Streamlit
st.set_page_config(page_title="IngenIAr Dashboard", page_icon=":brain:", layout="wide")

# Inicializa variables de estado
if "active_option" not in st.session_state:
    st.session_state.active_option = "Chat"  # Opción predeterminada

# CSS personalizado para estilizar los botones y la barra lateral
st.markdown(
    f"""
    <style>
    .stButton button {{
        width: 100%;  /* Hace los botones del mismo ancho que la barra lateral */
        background-color: #ff7f50;  /* Color naranja */
        color: white;  /* Color del texto */
        border-radius: 8px;  /* Bordes redondeados */
        padding: 10px 0px;  /* Aumenta el tamaño del botón */
        margin: 5px 0px;  /* Margen entre los botones */
        font-size: 16px;  /* Aumenta el tamaño del texto */
    }}

    .stButton button:hover {{
        background-color: #ff5733;  /* Un color más oscuro al pasar el mouse */
    }}

    /* Cambiar color del botón seleccionado */
    .stButton.selected button {{
        background-color: #4CAF50 !important;  /* Un color verde para el botón seleccionado */
        color: white !important;  /* Asegúrate de que el texto siga siendo blanco */
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Función para crear un botón estilizado que cambia a verde cuando está seleccionado
def sidebar_button(label, option):
    # Verifica si la opción actual es la seleccionada
    if st.session_state.active_option == option:
        btn_class = "selected"
    else:
        btn_class = ""

    # Crea un botón en la barra lateral con el estilo aplicado
    clicked = st.sidebar.markdown(f'<div class="stButton {btn_class}">{st.sidebar.button(label, key=option)}</div>', unsafe_allow_html=True)

    # Actualiza la opción activa si se hace clic en el botón
    if st.sidebar.button(label, key=f"{option}_click"):
        st.session_state.active_option = option

# Menú de botones en la barra lateral
st.sidebar.title("IngenIAr Dashboard")
st.sidebar.markdown("### Navega por las opciones:")

# Botones estilizados
sidebar_button("Chat", "Chat")
sidebar_button("Otra Opción", "Otra Opción")

# Mostrar la interfaz del chat si se selecciona "Chat"
if st.session_state.active_option == "Chat":
    st.subheader("🤖 IngenIAr - Chat")

    # Aquí iría el código de chat que ya has implementado
    st.write("Aquí está la interfaz de chat...")

# Mostrar contenido para "Otra Opción"
if st.session_state.active_option == "Otra Opción":
    st.subheader("Esta es otra opción.")
    st.write("Aquí puedes agregar más funcionalidades o información relacionada.")
