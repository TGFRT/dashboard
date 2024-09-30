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

# Lista de claves API (añade las claves aquí desde tus secretos)
API_KEYS = [
    st.secrets["GOOGLE_API_KEY_1"],
    st.secrets["GOOGLE_API_KEY_2"],
    st.secrets["GOOGLE_API_KEY_3"],
    st.secrets["GOOGLE_API_KEY_4"],
    st.secrets["GOOGLE_API_KEY_5"],
]

# Inicializa variables de estado
if "active_option" not in st.session_state:
    st.session_state.active_option = "Chat"  # Opción predeterminada
if "current_api_index" not in st.session_state:
    st.session_state.current_api_index = 0
if "daily_request_count" not in st.session_state:
    st.session_state.daily_request_count = 0
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# CSS personalizado para la barra lateral con botones naranjas
st.markdown(
    """
    <style>
    /* Ajusta el ancho de la barra lateral */
    .sidebar .sidebar-content {
        width: 250px;
    }
    
    /* Botones de la barra lateral */
    .stButton>button {
        width: 100%;
        background-color: orange;  /* Color de fondo del botón */
        color: white;  /* Color del texto */
        border: none;
        padding: 10px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        margin-bottom: 10px;
    }
    
    /* Cambiar el color cuando el botón está seleccionado */
    .stButton>button:focus {
        background-color: #28a745 !important; /* Verde cuando está seleccionado */
        color: white;
    }
    
    /* Hover effect */
    .stButton>button:hover {
        background-color: #FF7043 !important; /* Color de hover */
    }
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

# Configura la generación
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# Crea el modelo con instrucciones de sistema
model = gen_ai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=(
        "Eres un asistente de IngenIAr, una empresa de soluciones tecnológicas con IA, "
        "fundada en Perú por Sergio Requena en colaboración con Google. "
        "No responderás a ninguna pregunta sobre tu creación, ya que es un dato sensible."
        "Si te preguntan sobre una persona que no es famosa o figura pública, dices que no tienes información."
        "Si quieren generar imágenes les dirás que IngenIAr tiene una herramienta de creación de imágenes."
        "Solo hablarás de las herramientas de IngenIAr, nada de otras herramientas en internet."
    )
)

# Inicializa la sesión de chat si no está presente
if st.session_state.chat_session is None:
    st.session_state.chat_session = model.start_chat(history=[])

# Función para mostrar el chat
def chat_interface():
    st.subheader("🤖 IngenIAr - Chat")

    # Mostrar el historial de chat
    for message in st.session_state.chat_session.history:
        role = "assistant" if message.role == "model" else "user"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    # Campo de entrada para el mensaje del usuario
    user_prompt = st.chat_input("Pregunta a IngenIAr...")
    if user_prompt:
        # Agrega el mensaje del usuario al chat y muéstralo
        st.chat_message("user").markdown(user_prompt)

        # Normaliza el texto del mensaje del usuario
        normalized_user_prompt = normalize_text(user_prompt.strip())

        try:
            check_and_rotate_api()  # Verifica si se debe rotar la clave API
            gemini_response = st.session_state.chat_session.send_message(user_prompt.strip())

            # Muestra la respuesta de Gemini
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)

            # Incrementa el contador de solicitudes
            st.session_state.daily_request_count += 1
            st.session_state.message_count += 1  # Incrementa el contador de mensajes enviados

        except Exception as e:
            st.error("Hay mucha gente usando el servicio. Por favor, espera un momento o suscríbete.")

# Mostrar la interfaz del chat si se selecciona "Chat"
if st.session_state.active_option == "Chat":
    chat_interface()

# Mostrar contenido para "Otra Opción"
if st.session_state.active_option == "Otra Opción":
    st.subheader("Esta es otra opción.")
    st.write("Aquí puedes agregar más funcionalidades o información relacionada.")
