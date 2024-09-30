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
    st.title("CREA Y PLANIFICA CON INGENIAR 💡")

# Selección de la funcionalidad
option = st.selectbox("Elige una opción:", ("Generar Ideas de Negocio", "Generar Modelo de Negocio", "Planificador Financiero", "Validador de Ideas"))

# Barra de progreso al cambiar de opción
with st.spinner("Cargando..."):
    time.sleep(1)

if option == "Generar Ideas de Negocio":
    st.header("Cuéntanos sobre ti")

    # Cajas de texto para ingresar información del usuario
    intereses = st.text_area("¿Cuáles son tus intereses o pasiones?")
    experiencia = st.text_area("¿Cuál es tu experiencia laboral o académica?")
    conocimientos = st.text_area("¿En qué áreas tienes conocimientos o habilidades?")
    mercado = st.text_area("¿Qué tipo de mercado te interesa?")
    problemas = st.text_area("¿Qué problemas o necesidades quieres resolver?")

    # Botón para iniciar la generación de ideas
    if st.button("Generar Ideas"):
        if not (intereses and experiencia and conocimientos and mercado and problemas):
            st.error("Por favor, completa todos los campos antes de generar ideas.")
        else:
            prompt = f"""
            Genera 5 ideas de negocio innovadoras para una persona con las siguientes características:
            - Intereses: {intereses}
            - Experiencia: {experiencia}
            - Conocimientos: {conocimientos}
            - Mercado: {mercado}
            - Problemas a resolver: {problemas}
            
            Incluye una breve descripción de cada idea y su potencial mercado.
            """

            try:
                model = gen_ai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                    system_instruction="Eres un generador de ideas de negocio innovadoras."
                )

                chat_session = model.start_chat(history=[])

                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.05)  # Simulación de tiempo de espera
                    progress.progress(i + 1)

                gemini_response = chat_session.send_message(prompt)

                st.markdown(f"## Ideas de negocio:\n{gemini_response.text}")
            except Exception as e:
                st.error(f"Ocurrió un error al generar las ideas: {str(e)}")

elif option == "Generar Modelo de Negocio":
    st.header("Proporcione su idea de negocio")

    idea_negocio = st.text_area("Describe tu idea de negocio")

    if st.button("Generar Modelo de Negocio"):
        prompt = f"""
        Crea un modelo de negocio Canvas basado en la siguiente idea:
        
        Idea de negocio: {idea_negocio}

        Incluye los siguientes componentes:
        - Propuesta de valor
        - Segmentos de clientes
        - Fuentes de ingresos
        - Actividades clave
        - Recursos clave
        - Canales
        
        Además, proporciona sugerencias de estrategias para mejorar cada área.
        """

        try:
            model = gen_ai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                system_instruction="Eres un asistente para crear modelos de negocio Canvas."
            )

            chat_session = model.start_chat(history=[])

            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.05)  # Simulación de tiempo de espera
                progress.progress(i + 1)

            gemini_response = chat_session.send_message(prompt)

            st.markdown(f"## Modelo de Negocio Canvas Generado:\n{gemini_response.text}")
        except Exception as e:
            st.error(f"Error al generar el modelo de negocio: {str(e)}")

elif option == "Planificador Financiero":
    st.header("Planificador Financiero")

    # Entradas para ingresos y costos
    ingresos_fijos = st.number_input("Ingresos fijos proyectados:", min_value=0.0, step=100.0)
    ingresos_variables = st.number_input("Ingresos variables proyectados:", min_value=0.0, step=100.0)
    costos_fijos = st.number_input("Costos fijos proyectados:", min_value=0.0, step=100.0)
    costos_variables = st.number_input("Costos variables proyectados:", min_value=0.0, step=100.0)

    # Selección de moneda
    moneda = st.selectbox("Selecciona la moneda:", ["Dólares (USD)", "Soles (PEN)", "Euros (EUR)"])

    # Campo para describir el negocio
    descripcion_negocio = st.text_area("Describe tu negocio y su estructura:")

    # Subida de archivo PDF
    uploaded_file = st.file_uploader("Sube un archivo PDF con información adicional", type="pdf")

    if st.button("Generar Plan Financiero"):
        # Validación de entradas
        if ingresos_fijos < 0 or ingresos_variables < 0 or costos_fijos < 0 or costos_variables < 0:
            st.error("Por favor, ingresa valores válidos para ingresos y costos.")
        else:
            # Leer contenido del PDF si se sube uno
            pdf_content = ""
            if uploaded_file is not None:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    pdf_content += page.extract_text() + "\n"

            total_ingresos = ingresos_fijos + ingresos_variables
            total_costos = costos_fijos + costos_variables
            rentabilidad = total_ingresos - total_costos
            
            prompt = f"""
            Genera un plan financiero realista para un negocio con los siguientes datos:
            - Ingresos fijos proyectados: {ingresos_fijos} {moneda}
            - Ingresos variables proyectados: {ingresos_variables} {moneda}
            - Costos fijos proyectados: {costos_fijos} {moneda}
            - Costos variables proyectados: {costos_variables} {moneda}
            - Rentabilidad proyectada: {rentabilidad} {moneda}
            - Descripción del negocio: {descripcion_negocio}
            - Información adicional del PDF: {pdf_content}
            
            Proporciona un análisis de la rentabilidad y sugerencias para optimizar los costos.
            """

            try:
                model = gen_ai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                    system_instruction="Eres un planificador financiero. "
                                      "Proporciona un análisis realista basado en los datos proporcionados."
                )

                chat_session = model.start_chat(history=[])

                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.05)  # Simulación de tiempo de espera
                    progress.progress(i + 1)

                gemini_response = chat_session.send_message(prompt)

                st.markdown(f"## Plan Financiero Generado:\n{gemini_response.text}")
            except Exception as e:
                st.error(f"Error al generar el plan financiero: {str(e)}")

else:  # Opción: Validador de Ideas
    st.header("Validador de Ideas de Negocio")

    # Campo de entrada para la idea de negocio
    idea_negocio = st.text_area("Describe tu idea de negocio")

    # Botón para validar la idea
    if st.button("Validar Idea"):
        if not idea_negocio:
            st.error("Por favor, ingresa una descripción de tu idea de negocio.")
        else:
            prompt = f"""
            Evalúa la viabilidad de la siguiente idea de negocio:
            Idea de negocio: {idea_negocio}
            
            Proporciona comentarios sobre:
            - Oportunidades de mercado
            - Potenciales desafíos
            - Sugerencias para mejorar la idea
            """

            try:
                model = gen_ai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                    system_instruction="Eres un validador de ideas de negocio. "
                                      "Proporciona comentarios sobre la viabilidad de la idea presentada."
                )

                chat_session = model.start_chat(history=[])

                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.05)  # Simulación de tiempo de espera
                    progress.progress(i + 1)

                gemini_response = chat_session.send_message(prompt)

                st.markdown(f"## Comentarios sobre la Idea:\n{gemini_response.text}")
            except Exception as e:
                st.error(f"Ocurrió un error al validar la idea: {str(e)}")
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
