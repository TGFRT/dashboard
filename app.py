Claro, te proporcionaré el código completo del dashboard actualizado con todas las nuevas funcionalidades integradas.



```python
import os
import time
import streamlit as st
import google.generativeai as gen_ai
from datetime import datetime
from difflib import SequenceMatcher
import re
import PyPDF2

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
    st.session_state.last_reset_datetime = datetime.now()
if "last_user_messages" not in st.session_state:
    st.session_state.last_user_messages = []

# Configura la API con la clave actual
def configure_api():
    gen_ai.configure(api_key=API_KEYS[st.session_state.current_api_index])

# Rotar la clave API si alcanzas el límite diario
def rotate_api():
    st.session_state.current_api_index = (st.session_state.current_api_index + 1) % len(API_KEYS)
    st.session_state.daily_request_count = 0
    configure_api()

# Verificar y rotar si se alcanza el límite diario
def check_and_rotate_api():
    if st.session_state.daily_request_count >= 1500:
        st.warning(f"Clave API {API_KEYS[st.session_state.current_api_index]} alcanzó el límite diario. Rotando...")
        rotate_api()

# Verifica si se debe reiniciar el contador de mensajes
def check_reset():
    try:
        if datetime.now().date() > st.session_state.last_reset_datetime.date():
            st.session_state.daily_request_count = 0
            st.session_state.last_reset_datetime = datetime.now()
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
page = st.sidebar.radio("Selecciona una opción:", ["Chat", "Crea y Planifica con IngenIAr"])

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
        normalized_user_input = normalize_text(user_input.strip())

        st.chat_message("user").markdown(user_input)

        is_similar = any(similar(normalized_user_input, normalize_text(previous)) > 0.90 for previous in st.session_state.last_user_messages)
        if is_similar:
            st.warning("Por favor, no envíes mensajes repetitivos.")
        else:
            st.session_state.last_user_messages.append(normalized_user_input)
            if len(st.session_state.last_user_messages) > 10:
                st.session_state.last_user_messages.pop(0)

            try:
                check_and_rotate_api()
                gemini_response = st.session_state.chat_session.send_message(user_input.strip())
                
                with st.chat_message("assistant"):
                    st.markdown(gemini_response.text)

                st.session_state.daily_request_count += 1

            except Exception as e:
                st.error("Hay mucha gente usando esto. Por favor, espera un momento o suscríbete a un plan de pago.")

    if st.button("Borrar Conversación", key="delete_conversation"):
        st.session_state.chat_session = model.start_chat(history=[])
        st.session_state.last_user_messages.clear()
        st.session_state.daily_request_count = 0
        st.success("Conversación borrada.")

# Nueva sección: Crea y Planifica con IngenIAr
elif page == "Crea y Planifica con IngenIAr":
    st.header("💡 Crea y Planifica con IngenIAr")

    option = st.selectbox("Elige una opción:", ("Generar Ideas de Negocio", "Generar Modelo de Negocio", "Planificador Financiero", "Validador de Ideas"))

    with st.spinner("Cargando..."):
        time.sleep(1)

    if option == "Generar Ideas de Negocio":
        st.subheader("Cuéntanos sobre ti")

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
                    check_and_rotate_api()
                    model = gen_ai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        generation_config=generation_config,
                        system_instruction="Eres un generador de ideas de negocio innovadoras."
                    )

                    chat_session = model.start_chat(history=[])

                    progress = st.progress(0)
                    for i in range(100):
                        time.sleep(0.05)
                        progress.progress(i + 1)

                    gemini_response = chat_session.send_message(prompt)

                    st.markdown(f"## Ideas de negocio:\n{gemini_response.text}")
                except Exception as e:
                    st.error(f"Ocurrió un error al generar las ideas: {str(e)}")

    elif option == "Generar Modelo de Negocio":
        st.subheader("Proporcione su idea de negocio")

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
                check_and_rotate_api()
                model = gen_ai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                    system_instruction="Eres un asistente para crear modelos de negocio Canvas."
                )

                chat_session = model.start_chat(history=[])

                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.05)
                    progress.progress(i + 1)

                gemini_response = chat_session.send_message(prompt)

                st.markdown(f"## Modelo de Negocio Canvas Generado:\n{gemini_response.text}")
            except Exception as e:
                st.error(f"Error al generar el modelo de negocio: {str(e)}")

    elif option == "Planificador Financiero":
        st.subheader("Planificador Financiero")

        ingresos_fijos = st.number_input("Ingresos fijos proyectados:", min_value=0.0, step=100.0)
        ingresos_variables = st.number_input("Ingresos variables proyectados:", min_value=0.0, step=100.0)
        costos_fijos = st.number_input("Costos fijos proyectados:", min_value=0.0, step=100.0)
        costos_variables = st.number_input("Costos variables proyectados:", min_value=0.0, step=100.0)

        moneda = st.selectbox("Selecciona la moneda:", ["Dólares (USD)", "Soles (PEN)", "Euros (EUR)"])

        descripcion_negocio = st.text_area("Describe tu negocio y su estructura:")

        uploaded_file = st.file_uploader("Sube un archivo PDF con información adicional", type="pdf")

        if st.button("Generar Plan Financiero"):
            if ingresos_fijos < 0 or ingresos_variables < 0 or costos_fijos < 0 or costos_variables < 0:
                st.error("Por favor, ingresa valores válidos para ingresos y costos.")
            else:
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
                    check_and_rotate_api()
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

```
