import os
import time
import streamlit as st
import google.generativeai as gen_ai
from datetime import datetime
from difflib import SequenceMatcher
import re
import PyPDF2
import requests
import io
from PIL import Image
import random
from googletrans import Translator

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
    page_title="IngenIAr",
    page_icon=":brain:",
    layout="centered",
)

# Selección de la funcionalidad
option = st.sidebar.selectbox("Elige una opción:", 
                               ("Chat con IngenIAr", 
                                "Creador de Contenido", 
                                "Creador de Campañas de Marketing"))

# API keys y configuración
API_KEYS = [st.secrets["GOOGLE_API_KEY_1"],
            st.secrets["GOOGLE_API_KEY_2"],
            st.secrets["GOOGLE_API_KEY_3"],
            st.secrets["GOOGLE_API_KEY_4"],
            st.secrets["GOOGLE_API_KEY_5"]]

# Inicializa variables de estado
if "current_api_index" not in st.session_state:
    st.session_state.current_api_index = 0
if "daily_request_count" not in st.session_state:
    st.session_state.daily_request_count = 0
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
if "last_reset_datetime" not in st.session_state:
    st.session_state.last_reset_datetime = datetime.now()  
if "last_user_messages" not in st.session_state:
    st.session_state.last_user_messages = []

# Configura la API con la clave actual
def configure_api():
    gen_ai.configure(api_key=API_KEYS[st.session_state.current_api_index])

# Resto del código...
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
    system_instruction="Eres un asistente de IngenIAr, una empresa de soluciones tecnológicas con IA."
)

# Chat con IngenIAr
if option == "Chat con IngenIAr":
    # Inicializa la sesión de chat si no está presente
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    st.title("🤖 IngenIAr - Chat")

    # Mostrar el historial de chat
    for message in st.session_state.chat_session.history:
        role = "assistant" if message.role == "model" else "user"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    # Botón para borrar la conversación
    if st.button("Borrar Conversación"):
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.last_user_messages.clear()
        st.session_state.message_count = 0
        st.session_state.daily_request_count = 0
        st.success("Conversación borrada.")

    # Campo de entrada para el mensaje del usuario
    user_input = st.chat_input("Pregunta a IngenIAr...")
    if user_input:
        normalized_user_input = normalize_text(user_input.strip())

        # Verificar si se ha alcanzado el límite de mensajes
        if st.session_state.message_count >= 20:
            st.warning("Has alcanzado el límite de 20 mensajes. Por favor, espera hasta mañana.")
        else:
            st.chat_message("user").markdown(user_input)

            is_similar = any(similar(normalized_user_input, normalize_text(previous)) > 0.90 for previous in st.session_state.last_user_messages)
            if is_similar:
                st.warning("Por favor, no envíes mensajes repetitivos.")
            else:
                st.session_state.last_user_messages.append(normalized_user_input)
                if len(st.session_state.last_user_messages) > 10:
                    st.session_state.last_user_messages.pop(0)

                try:
                    gemini_response = st.session_state.chat_session.send_message(user_input.strip())
                    with st.chat_message("assistant"):
                        st.markdown(gemini_response.text)

                    st.session_state.daily_request_count += 1
                    st.session_state.message_count += 1

                except Exception as e:
                    st.error("Hay mucha gente usando esto. Por favor, espera un momento o suscríbete a un plan de pago.")

# Creador de Contenido
elif option == "Creador de Contenido":
    st.header("Creador de Contenido")
    tema = st.text_area("Introduce el tema del contenido que deseas generar:")
    tipo_contenido = st.selectbox("Selecciona el tipo de contenido:", ["Artículo", "Publicación para Redes Sociales", "Boletín", "Anuncio"])

    imagen_opcion = st.radio("¿Quieres generar una imagen o subir una existente?", ("Generar Imagen", "Subir Imagen"))
    uploaded_image = None
    if imagen_opcion == "Subir Imagen":
        uploaded_image = st.file_uploader("Sube una imagen (formato: .jpg, .png)", type=["jpg", "png"])

    if st.button("Generar Contenido"):
        if not tema:
            st.error("Por favor, ingresa un tema para generar contenido.")
        else:
            prompt = f"""
            Genera un {tipo_contenido.lower()} sobre el siguiente tema:
            Tema: {tema}
            """
            try:
                chat_session = model.start_chat(history=[])
                gemini_response = chat_session.send_message(prompt)

                st.markdown(f"### Contenido Generado:\n")
                st.text_area("Texto generado:", value=gemini_response.text, height=200, key="generated_content", help="Puedes copiar el texto generado seleccionándolo.", disabled=False)

                if imagen_opcion == "Generar Imagen":
                    translator = Translator()
                    translated_prompt = translator.translate(tema, src='es', dest='en').text
                    prompt_suffix = f" with vibrant colors {random.randint(1, 1000)}"
                    final_prompt = translated_prompt + prompt_suffix

                    with st.spinner("Generando imagen..."):
                        image_response = requests.post("https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
                                                        headers={"Authorization": "Bearer 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"},
                                                        json={"inputs": final_prompt})

                        if image_response.status_code == 200:
                            st.session_state.image = Image.open(io.BytesIO(image_response.content))
                            st.image(st.session_state.image, caption="Imagen Generada", use_column_width=True)
                        else:
                            st.error("Hubo un problema al generar la imagen.")

                elif uploaded_image is not None:
                    st.image(uploaded_image, caption="Imagen Subida", use_column_width=True)

            except Exception as e:
                st.error(f"Ocurrió un error al generar el contenido: {str(e)}")

# Creador de Campañas de Marketing
elif option == "Creador de Campañas de Marketing":
    st.header("Creador de Campañas de Marketing")
    objetivos = st.text_area("Introduce los objetivos de tu campaña de marketing:")
    mensaje = st.text_area("¿Qué mensaje quieres transmitir en tu campaña?")

    if st.button("Generar Estrategia de Marketing"):
        if not objetivos or not mensaje:
            st.error("Por favor, completa todos los campos antes de generar la estrategia.")
        else:
            prompt = f"""
            Crea una estrategia de marketing basada en los siguientes objetivos y mensajes:
            Objetivos: {objetivos}
            Mensaje: {mensaje}
            """
            try:
                chat_session = model.start_chat(history=[])
                gemini_response = chat_session.send_message(prompt)

                st.markdown(f"### Estrategia de Marketing Generada:\n")
                st.text_area("Estrategia generada:", value=gemini_response.text, height=200, key="marketing_strategy", help="Puedes copiar la estrategia generada seleccionándola.", disabled=False)

            except Exception as e:
                st.error(f"Ocurrió un error al generar la estrategia: {str(e)}")
