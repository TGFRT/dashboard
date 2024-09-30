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
                                "Planifica tu negocio", 
                                "Marketing y ventas"))

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
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    st.title("🤖 IngenIAr - Chat")

    for message in st.session_state.chat_session.history:
        role = "assistant" if message.role == "model" else "user"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    if st.button("Borrar Conversación"):
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.last_user_messages.clear()
        st.session_state.message_count = 0
        st.session_state.daily_request_count = 0
        st.success("Conversación borrada.")

    user_input = st.chat_input("Pregunta a IngenIAr...")
    if user_input:
        normalized_user_input = normalize_text(user_input.strip())

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
elif option == "Planifica tu negocio":
    st.title("CREA Y PLANIFICA CON INGENIAR 💡")
    option = st.selectbox("Elige una opción:", ("Generar Ideas de Negocio", "Generar Modelo de Negocio", "Planificador Financiero", "Validador de Ideas"))

    with st.spinner("Cargando..."):
        time.sleep(1)

    if option == "Generar Ideas de Negocio":
        st.header("Cuéntanos sobre ti")

        intereses = st.text_area("¿Cuáles son tus intereses o pasiones?")
        experiencia = st.text_area("¿Cuál es tu experiencia laboral o académica?")
        conocimientos = st.text_area("¿En qué áreas tienes conocimientos o habilidades?")
        mercado = st.text_area("¿Qué tipo de mercado te interesa?")
        problemas = st.text_area("¿Qué problemas o necesidades quieres resolver?")

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

        ingresos_fijos = st.number_input("Ingresos fijos proyectados:", min_value=0.0, step=100.0)
        ingresos_variables = st.number_input("Ingresos variables proyectados:", min_value=0.0, step=100.0)
        costos_fijos = st.number_input("Costos fijos proyectados:", min_value=0.0, step=100.0)
        costos_variables = st.number_input("Costos variables proyectados:", min_value=0.0, step=100.0)

        moneda = st.selectbox("Selecciona la moneda:", ["Dólares (USD)", "Soles (PEN)", "Euros (EUR)"])

        descripcion_negocio = st.text_area("Describe tu negocio y su estructura:")
        uploaded_file = st.file_uploader("Sube un archivo PDF con información adicional", type="pdf")

        if st.button("Generar Plan Financiero"):
            if ingresos_fijos < 0 or ingresos_variables < 0 or costos_fijos < 0 or costos_variables < 0:
                st.error("Los ingresos y costos deben ser valores no negativos.")
            else:
                prompt = f"""
                Genera un plan financiero para un negocio con las siguientes características:
                - Ingresos fijos proyectados: {ingresos_fijos}
                - Ingresos variables proyectados: {ingresos_variables}
                - Costos fijos proyectados: {costos_fijos}
                - Costos variables proyectados: {costos_variables}
                - Moneda: {moneda}
                - Descripción del negocio: {descripcion_negocio}
                """

                if uploaded_file is not None:
                    with io.BytesIO(uploaded_file.read()) as pdf_file:
                        reader = PyPDF2.PdfReader(pdf_file)
                        num_pages = len(reader.pages)
                        st.write(f"Número de páginas en el PDF: {num_pages}")

                        texto_pdf = ""
                        for page in reader.pages:
                            texto_pdf += page.extract_text() + "\n"

                    prompt += f"\n\nInformación adicional del PDF:\n{texto_pdf}"

                try:
                    model = gen_ai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        generation_config=generation_config,
                        system_instruction="Eres un asistente para crear planes financieros."
                    )

                    chat_session = model.start_chat(history=[])

                    progress = st.progress(0)
                    for i in range(100):
                        time.sleep(0.05)  # Simulación de tiempo de espera
                        progress.progress(i + 1)

                    gemini_response = chat_session.send_message(prompt)

                    st.markdown(f"## Plan Financiero Generado:\n{gemini_response.text}")
                except Exception as e:
                    st.error(f"Ocurrió un error al generar el plan financiero: {str(e)}")

    elif option == "Validador de Ideas":
        st.header("Validador de Ideas")

        idea = st.text_area("Describe tu idea")

        if st.button("Validar Idea"):
            prompt = f"""
            Analiza y proporciona retroalimentación sobre la siguiente idea:
            {idea}
            """

            try:
                model = gen_ai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                    system_instruction="Eres un asistente para validar ideas de negocio."
                )

                chat_session = model.start_chat(history=[])

                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.05)  # Simulación de tiempo de espera
                    progress.progress(i + 1)

                gemini_response = chat_session.send_message(prompt)

                st.markdown(f"## Retroalimentación sobre la Idea:\n{gemini_response.text}")
            except Exception as e:
                st.error(f"Ocurrió un error al validar la idea: {str(e)}")

# Creador de Campañas de Marketing
elif option == "Marketing y ventas":
    def query(payload):
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": "Bearer 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"}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response

# Título de la web
st.title("CREADOR DE MARKETING CON INGENIAR 🚀")

# Selección de la funcionalidad
option = st.selectbox("Elige una opción:", ("Creador de Contenido", "Analizador de Audiencia", "Creador de Campañas de Marketing"))

# Barra de progreso al cambiar de opción
with st.spinner("Cargando..."):
    time.sleep(1)

if option == "Creador de Contenido":
    st.header("Creador de Contenido")

    tema = st.text_area("Introduce el tema del contenido que deseas generar:")
    tipo_contenido = st.selectbox("Selecciona el tipo de contenido:", ["Artículo", "Publicación para Redes Sociales", "Boletín", "Anuncio"])

    # Opción para generar o subir imagen
    imagen_opcion = st.radio("¿Quieres generar una imagen o subir una existente?", ("Generar Imagen", "Subir Imagen"))

    # Subida de imagen si se elige subir
    uploaded_image = None
    if imagen_opcion == "Subir Imagen":
        uploaded_image = st.file_uploader("Sube una imagen (formato: .jpg, .png)", type=["jpg", "png"])

    # Botón para generar contenido
    if st.button("Generar Contenido"):
        if not tema:
            st.error("Por favor, ingresa un tema para generar contenido.")
        else:
            prompt = f"""
            Genera un {tipo_contenido.lower()} sobre el siguiente tema:
            Tema: {tema}
            """

            try:
                model = gen_ai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                    system_instruction="Eres un generador de contenido de marketing."
                )

                chat_session = model.start_chat(history=[])

                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.05)  # Simulación de tiempo de espera
                    progress.progress(i + 1)

                gemini_response = chat_session.send_message(prompt)

                # Mostrar el contenido generado con opción de copiar
                st.markdown(f"### Contenido Generado:\n")
                st.text_area("Texto generado:", value=gemini_response.text, height=200, key="generated_content", help="Puedes copiar el texto generado seleccionándolo.", disabled=False)

                # Si el usuario eligió generar una imagen
                if imagen_opcion == "Generar Imagen":
                    # Generación de imagen basada en el tema
                    translator = Translator()
                    translated_prompt = translator.translate(tema, src='es', dest='en').text
                    prompt_suffix = f" with vibrant colors {random.randint(1, 1000)}"
                    final_prompt = translated_prompt + prompt_suffix

                    # Generar la imagen usando la función query
                    with st.spinner("Generando imagen..."):
                        image_response = query({"inputs": final_prompt})

                    # Manejo de errores
                    if image_response.status_code == 429:
                        st.error("Error 429: Has alcanzado el límite de uso gratuito. Considera suscribirte a IngenIAr mensual.")
                    elif image_response.status_code != 200:
                        st.error("Hubo un problema al generar la imagen. Intenta de nuevo más tarde.")
                    else:
                        # Abrir la imagen desde la respuesta
                        st.session_state.image = Image.open(io.BytesIO(image_response.content))

                        # Mostrar la imagen generada
                        st.image(st.session_state.image, caption="Imagen Generada", use_column_width=True)

                elif uploaded_image is not None:
                    # Mostrar la imagen subida
                    st.image(uploaded_image, caption="Imagen Subida", use_column_width=True)
                else:
                    st.success("No se generó ninguna imagen y no se subió ninguna.")

            except Exception as e:
                st.error(f"Ocurrió un error al generar el contenido: {str(e)}")

elif option == "Analizador de Audiencia":
    st.header("Analizador de Audiencia")

    # Entradas para datos del público objetivo
    datos_publico = st.text_area("Ingresa datos sobre tu público objetivo (intereses, comportamientos, etc.):")

    # Subida de archivo PDF
    uploaded_file = st.file_uploader("Sube un archivo PDF con estadísticas adicionales", type="pdf")

    # Botón para analizar audiencia
    if st.button("Analizar Audiencia"):
        if not datos_publico:
            st.error("Por favor, ingresa información sobre tu público objetivo.")
        else:
            # Leer contenido del PDF si se sube uno
            pdf_content = ""
            if uploaded_file is not None:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    pdf_content += page.extract_text() + "\n"

            prompt = f"""
            Analiza la siguiente información sobre mi público objetivo:
            Datos del público: {datos_publico}
            Información adicional del PDF: {pdf_content}
            
            Proporciona un análisis de sus necesidades, intereses y hábitos de consumo.
            """

            try:
                model = gen_ai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                    system_instruction="Eres un analizador de audiencia de marketing."
                )

                chat_session = model.start_chat(history=[])

                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.05)  # Simulación de tiempo de espera
                    progress.progress(i + 1)

                gemini_response = chat_session.send_message(prompt)

                # Mostrar el análisis generado con opción de copiar
                st.markdown(f"### Análisis de Audiencia Generado:\n")
                st.text_area("Análisis generado:", value=gemini_response.text, height=200, key="audiencia_content", help="Puedes copiar el análisis generado seleccionándolo.", disabled=False)

            except Exception as e:
                st.error(f"Ocurrió un error al analizar la audiencia: {str(e)}")

else:  # Opción: Creador de Campañas de Marketing
    st.header("Creador de Campañas de Marketing")

    # Entradas para la campaña
    objetivos = st.text_area("Introduce los objetivos de tu campaña de marketing:")
    mensaje = st.text_area("¿Qué mensaje quieres transmitir en tu campaña?")

    # Botón para generar estrategia de marketing
    if st.button("Generar Estrategia de Marketing"):
        if not objetivos or not mensaje:
            st.error("Por favor, completa todos los campos antes de generar la estrategia.")
        else:
            prompt = f"""
            Crea una estrategia de marketing basada en los siguientes objetivos y mensajes:
            Objetivos: {objetivos}
            Mensaje: {mensaje}
            
            Proporciona sugerencias sobre plataformas, canales y mensajes específicos para alcanzar a la audiencia.
            """

            try:
                model = gen_ai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                    system_instruction="Eres un creador de campañas de marketing."
                )

                chat_session = model.start_chat(history=[])

                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.05)  # Simulación de tiempo de espera
                    progress.progress(i + 1)

                gemini_response = chat_session.send_message(prompt)

                # Mostrar la estrategia generada con opción de copiar
                st.markdown(f"### Estrategia de Marketing Generada:\n")
                st.text_area("Estrategia generada:", value=gemini_response.text, height=200, key="marketing_strategy", help="Puedes copiar la estrategia generada seleccionándola.", disabled=False)

            except Exception as e:
                st.error(f"Ocurrió un error al generar la estrategia: {str(e)}")

