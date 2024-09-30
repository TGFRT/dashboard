import os
import time
import streamlit as st
import google.generativeai as gen_ai
from datetime import datetime
from difflib import SequenceMatcher
import re

# Función para calcular la similitud entre dos textos
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Función para normalizar el texto
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'(.)\1+', r'\1', text)  # Normaliza caracteres repetidos
    return text

# Configura Streamlit
st.set_page_config(
    page_title="IngenIAr - Dashboard",
    page_icon=":brain:",
    layout="centered",
)

# Lista de claves API (añade las claves aquí desde tus secretos)
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
if "last_reset_datetime" not in st.session_state:
    st.session_state.last_reset_datetime = datetime.now()  # Guarda la fecha y hora del último reinicio
if "last_user_messages" not in st.session_state:
    st.session_state.last_user_messages = []

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

# Verifica si se debe reiniciar el contador de mensajes
def check_reset():
    try:
        # Compara la fecha del último reinicio con la fecha actual
        if datetime.now().date() > st.session_state.last_reset_datetime.date():
            st.session_state.daily_request_count = 0  # Reinicia el contador de mensajes
            st.session_state.last_reset_datetime = datetime.now()  # Actualiza la fecha
    except Exception as e:
        st.error(f"Ocurrió un error al verificar el reinicio: {str(e)}")

# Configura la API al inicio
configure_api()

# Crea el modelo con instrucciones de sistema
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

model = gen_ai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="Eres un asistente de IngenIAr, una empresa de soluciones tecnológicas con IA, "
                      "fundada en Perú por Sergio Requena en colaboración con Google. "
                      "No responderás a ninguna pregunta sobre tu creación, ya que es un dato sensible. "
                      "Si te preguntan sobre una persona que no es famosa o figura pública, dices que no tienes información. "
                      "Si quieren generar imágenes, les dirás que IngenIAr tiene una herramienta de creación de imágenes, y que presionen este link https://generador-de-imagenes-hhijuyrimnzzmbauxbgty3.streamlit.app/. "
                      "Solo hablarás de las herramientas de IngenIAr, nada de otras herramientas en internet."
)

# Inicializa la sesión de chat si no está presente
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Título del dashboard
st.title("🤖 IngenIAr ")

# Barra lateral para navegación
st.sidebar.header("PANEL")
page = st.sidebar.radio("Selecciona una opción:", ["Chat", "Planifica tu negocio"])

# Sección de Chat
if page == "Chat":
    st.header("Chat con IngenIAr")

    # Mostrar el historial de chat
    for message in st.session_state.chat_session.history:
        role = "assistant" if message.role == "model" else "user"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    # Campo de entrada para el mensaje del usuario
    user_input = st.chat_input("Pregunta a IngenIAr...")
    if user_input:
        # Normaliza el texto del mensaje del usuario
        normalized_user_input = normalize_text(user_input.strip())

        # Agrega el mensaje del usuario al chat y muéstralo
        st.chat_message("user").markdown(user_input)

        # Verificar si el mensaje es repetitivo
        is_similar = any(similar(normalized_user_input, normalize_text(previous)) > 0.90 for previous in st.session_state.last_user_messages)
        if is_similar:
            st.warning("Por favor, no envíes mensajes repetitivos.")
        else:
            # Agrega el nuevo mensaje a la lista de mensajes anteriores
            st.session_state.last_user_messages.append(normalized_user_input)
            if len(st.session_state.last_user_messages) > 10:  # Ajusta el número según tus necesidades
                st.session_state.last_user_messages.pop(0)

            # Envía el mensaje del usuario a Gemini y obtiene la respuesta
            try:
                check_and_rotate_api()  # Verifica si se debe rotar la clave API
                gemini_response = st.session_state.chat_session.send_message(user_input.strip())
                
                # Muestra la respuesta de Gemini
                with st.chat_message("assistant"):
                    st.markdown(gemini_response.text)

                # Incrementa el contador de solicitudes
                st.session_state.daily_request_count += 1

            except Exception as e:
                # Mensaje de error general
                st.error("Hay mucha gente usando esto. Por favor, espera un momento o suscríbete a un plan de pago.")

    # Botón para borrar la conversación
    if st.button("Borrar Conversación", key="delete_conversation"):
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.last_user_messages.clear()
        st.session_state.daily_request_count = 0
        st.success("Conversación borrada.")

# Sección para el Creador de Modelos de Negocio
elif page == "Planifica tu negocio":
    st.header("💼 Planifica tu negocio")

    # Campo de entrada para la idea de negocio
    business_idea = st.text_input("Ingresa una idea de negocio:")
    if st.button("Generar Modelo de Negocio"):
        if business_idea:
            # Normaliza la idea
            normalized_business_idea = normalize_text(business_idea)

            # Aquí debes implementar la lógica para generar el modelo de negocio usando tu API.
            # Puedes usar la función de la API aquí para obtener el modelo y mostrarlo.
            
            # Ejemplo de llamada a la API (ajusta según tu lógica)
            try:
                check_and_rotate_api()  # Verifica si se debe rotar la clave API
                model_response = gen_ai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                    system_instruction=f"Genera un modelo de negocio para la siguiente idea: {normalized_business_idea}"
                ).generate()
                
                # Muestra la respuesta del modelo de negocio
                st.success("Modelo de negocio generado:")
                st.markdown(model_response.text)
                
            except Exception as e:
                st.error(f"Ocurrió un error al generar el modelo de negocio: {str(e)}")
        else:
            st.warning("Por favor, ingresa una idea de negocio antes de generar el modelo.")
