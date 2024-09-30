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

# CSS personalizado para la barra lateral
st.markdown(
    f"""
    <style>
    .sidebar .sidebar-content {{
        width: 250px;  /* Ancho de la barra lateral */
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Función para crear un botón en la barra lateral
def sidebar_button(label, option):
    # Verifica si la opción actual está seleccionada
    if st.session_state.active_option == option:
        st.sidebar.button(label, key=option)
    else:
        if st.sidebar.button(label, key=option):
            st.session_state.active_option = option

# Menú de botones en la barra lateral
st.sidebar.title("IngenIAr Dashboard")
st.sidebar.markdown("### Navega por las opciones:")

# Botones en la barra lateral
sidebar_button("Chat", "Chat")
sidebar_button("Otra Opción", "Otra Opción")

# Mostrar la interfaz del chat si se selecciona "Chat"
if st.session_state.active_option == "Chat":
    st.subheader("🤖 IngenIAr - Chat")

    # Aquí iría el código del chat que ya has implementado
    st.write("Aquí está la interfaz de chat...")

# Mostrar contenido para "Otra Opción"
if st.session_state.active_option == "Otra Opción":
    st.subheader("Esta es otra opción.")
    st.write("Aquí puedes agregar más funcionalidades o información relacionada.")
