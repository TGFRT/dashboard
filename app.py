import os
import time
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

# Lista de claves API
API_KEYS = [
    st.secrets["GOOGLE_API_KEY_1"],
    st.secrets["GOOGLE_API_KEY_2"],
    st.secrets["GOOGLE_API_KEY_3"],
    st.secrets["GOOGLE_API_KEY_4"],
    st.secrets["GOOGLE_API_KEY_5"],
]

# Inicializa variables de estado
if "current_api_index" not in st.session_state:
    st.session_state.current_api_index = 0
if "daily_request_count" not in st.session_state:
    st.session_state.daily_request_count = 0
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
if "waiting" not in st.session_state:
    st.session_state.waiting = False
if "last_user_messages" not in st.session_state:
    st.session_state.last_user_messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# Configura la API con la clave actual
def configure_api():
    gen_ai.configure(api_key=API_KEYS[st.session_state.current_api_index])

# Rotar la clave API si alcanzas el límite diario
def rotate_api():
    st.session_state.current_api_index = (st.session_state.current_api_index + 1) % len(API_KEYS)
    st.session_state.daily_request_count = 0  # Reinicia el conteo de solicitudes diarias
    configure_api()

# Verificar y rotar si se alcanza el límite diario
def check_and_rotate_api():
    if st.session_state.daily_request_count >= 1500:  # Límite diario
        st.warning(f"Clave API {API_KEYS[st.session_state.current_api_index]} alcanzó el límite diario. Rotando...")
        rotate_api()

# Inicializa el modelo de IA
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# Asegúrate de que el modelo esté inicializado
try:
    model = gen_ai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction="Eres un asistente de IngenIAr, una empresa de soluciones tecnológicas..."
    )
except Exception as e:
    st.error(f"Error al inicializar el modelo: {str(e)}")

# Inicializa la sesión de chat
if st.session_state.chat_session is None:
    try:
        st.session_state.chat_session = model.start_chat(history=[])
    except Exception as e:
        st.error(f"Error al iniciar la sesión de chat: {str(e)}")

# Menú de navegación en la parte izquierda
st.sidebar.title("IngenIAr Dashboard")
st.sidebar.markdown("### Navega por las opciones:")

# Opciones del menú
option = st.sidebar.radio("Selecciona una opción:", ("Chat", "Otra Opción"))

# Si elige "Chat", muestra la interfaz del chat
if option == "Chat":
    st.subheader("🤖 IngenIAr - Chat")

    # Mostrar el historial de chat solo si chat_session y history existen
    if st.session_state.chat_session and hasattr(st.session_state.chat_session, "history"):
        for message in st.session_state.chat_session.history:
            role = "assistant" if message.role == "model" else "user"
            with st.chat_message(role):
                st.markdown(message.parts[0].text)

    # Campo de entrada para el mensaje del usuario
    user_prompt = st.chat_input("Pregunta a IngenIAr...")
    if user_prompt:
        st.chat_message("user").markdown(user_prompt)
        normalized_user_prompt = normalize_text(user_prompt.strip())
        st.session_state.last_user_messages.append(normalized_user_prompt)

        # Verificar si el mensaje es repetitivo
        is_similar = any(similar(normalized_user_prompt, normalize_text(previous)) > 0.90 for previous in st.session_state.last_user_messages)
        if is_similar:
            st.warning("Por favor, no envíes mensajes repetitivos.")
        else:
            # Envía el mensaje del usuario a Gemini
            try:
                check_and_rotate_api()  # Verifica si se debe rotar la clave API
                gemini_response = st.session_state.chat_session.send_message(user_prompt.strip())
                with st.chat_message("assistant"):
                    st.markdown(gemini_response.text)

                st.session_state.daily_request_count += 1
                st.session_state.message_count += 1

            except Exception as e:
                st.error("Hay muchas personas usando esto. Por favor, espera un momento o suscríbete a un plan de pago.")

# Puedes agregar aquí más lógica para la "Otra Opción"
if option == "Otra Opción":
    st.subheader("Esta es otra opción.")
    st.write("Aquí puedes agregar más funcionalidades o información relacionada.")
