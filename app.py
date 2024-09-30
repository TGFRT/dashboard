
import streamlit as st
import google.generativeai as gen_ai
from datetime import datetime
import re
from difflib import SequenceMatcher

# Función para calcular la similitud entre dos textos
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Función para normalizar el texto
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Eliminar signos de puntuación
    return text

# Configura Streamlit
st.set_page_config(page_title="Dashboard de IngenIAr", page_icon=":brain:")

# Título del dashboard
st.title("Dashboard de IngenIAr")

# Menú lateral para elegir opciones
option = st.sidebar.selectbox("Selecciona una opción", ["Chat", "Opción 2", "Opción 3"])

# Inicializa variables de estado
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "daily_request_count" not in st.session_state:
    st.session_state.daily_request_count = 0

# Configura la API (aquí van tus claves API)
API_KEYS = [
    st.secrets["GOOGLE_API_KEY_1"],
    st.secrets["GOOGLE_API_KEY_2"],
    st.secrets["GOOGLE_API_KEY_3"],
    st.secrets["GOOGLE_API_KEY_4"],
    st.secrets["GOOGLE_API_KEY_5"]
]

def configure_api():
    gen_ai.configure(api_key=API_KEYS[0])  # Usar la primera clave por defecto

def chat_interface():
    st.subheader("🤖 IngenIAr - Chat")

    # Inicializa la sesión de chat si no está presente
    if st.session_state.chat_session is None:
        st.session_state.chat_session = model.start_chat(history=[])

    # Mostrar el historial de chat
    if st.session_state.chat_session:
        for message in st.session_state.chat_session.history:
            role = "assistant" if message.role == "model" else "user"
            with st.chat_message(role):
                st.markdown(message.parts[0].text)

    # Campo de entrada para el mensaje del usuario
    user_prompt = st.chat_input("Pregunta a IngenIAr...")
    if user_prompt:
        # Normaliza el texto del mensaje del usuario
        normalized_user_prompt = normalize_text(user_prompt.strip())
        # Envía el mensaje del usuario a Gemini y obtiene la respuesta
        try:
            gemini_response = st.session_state.chat_session.send_message(user_prompt.strip())
            # Muestra la respuesta de Gemini
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)
            st.session_state.daily_request_count += 1  # Incrementa el contador de solicitudes
        except Exception as e:
            st.error("Hay muchas personas usando esto. Por favor, espera un momento o suscríbete a un plan de pago.")

# Lógica para mostrar el chat o las otras opciones
if option == "Chat":
    configure_api()  # Configura la API antes de iniciar el chat
    chat_interface()
elif option == "Opción 2":
    st.subheader("Contenido de la Opción 2")
    # Aquí puedes agregar más funcionalidades
elif option == "Opción 3":
    st.subheader("Contenido de la Opción 3")
    # Aquí puedes agregar más funcionalidades
