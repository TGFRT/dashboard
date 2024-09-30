import streamlit as st
import google.generativeai as gen_ai
from difflib import SequenceMatcher
import re
import time
import PyPDF2

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
    .sidebar .sidebar-content {
        width: 250px;
    }
    
    .stButton>button {
        width: 100%;
        background-color: orange;  
        color: white;
        border: none;
        padding: 10px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        margin-bottom: 10px;
    }
    
    .stButton>button:focus {
        background-color: #28a745 !important;
        color: white;
    }
    
    .stButton>button:hover {
        background-color: #FF7043 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Función para crear un botón en la barra lateral
def sidebar_button(label, option):
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
    st.session_state.daily_request_count = 0  
    configure_api()

# Verificar y rotar si se alcanza el límite diario
def check_and_rotate_api():
    if st.session_state.daily_request_count >= 1500:
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

    for message in st.session_state.chat_session.history:
        role = "assistant" if message.role == "model" else "user"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    user_prompt = st.chat_input("Pregunta a IngenIAr...")
    if user_prompt:
        st.chat_message("user").markdown(user_prompt)
        normalized_user_prompt = normalize_text(user_prompt.strip())

        try:
            check_and_rotate_api()
            gemini_response = st.session_state.chat_session.send_message(user_prompt.strip())
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)

            st.session_state.daily_request_count += 1
            st.session_state.message_count += 1
        except Exception as e:
            st.error("Hay mucha gente usando el servicio. Por favor, espera un momento o suscríbete.")

# Mostrar la interfaz del chat si se selecciona "Chat"
if st.session_state.active_option == "Chat":
    chat_interface()

# Mostrar contenido para "Otra Opción"
if st.session_state.active_option == "Otra Opción":
    st.subheader("CREA Y PLANIFICA CON INGENIAR")

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
                        time.sleep(0.05)
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
                    time.sleep(0.05)
                    progress.progress(i + 1)

                gemini_response = chat_session.send_message(prompt)

                st.markdown(f"## Modelo de negocio Canvas:\n{gemini_response.text}")
            except Exception as e:
                st.error(f"Ocurrió un error al generar el modelo de negocio: {str(e)}")

    elif option == "Planificador Financiero":
        st.header("Planificador Financiero")

        ingresos = st.number_input("Ingrese los ingresos estimados mensuales:", min_value=0.0, format="%.2f")
        costos = st.number_input("Ingrese los costos estimados mensuales:", min_value=0.0, format="%.2f")

        archivo_pdf = st.file_uploader("Sube un archivo PDF con información adicional (opcional)", type="pdf")

        if st.button("Generar Plan Financiero"):
            if archivo_pdf:
                try:
                    pdf_reader = PyPDF2.PdfReader(archivo_pdf)
                    texto_completo = ""
                    for page in range(len(pdf_reader.pages)):
                        texto_completo += pdf_reader.pages[page].extract_text()

                    st.markdown(f"**Texto extraído del PDF:**\n\n{texto_completo}")
                except Exception as e:
                    st.error(f"Error al procesar el PDF: {str(e)}")

            if ingresos and costos:
                ganancia = ingresos - costos
                st.write(f"Ganancia mensual estimada: ${ganancia:.2f}")
            else:
                st.error("Por favor, ingrese los ingresos y costos para calcular la ganancia.")

    elif option == "Validador de Ideas":
        st.header("Validador de Ideas")

        idea_negocio = st.text_area("Describe tu idea de negocio")

        if st.button("Validar Idea"):
            if not idea_negocio:
                st.error("Por favor, ingrese una idea de negocio para validar.")
            else:
                prompt = f"""
                Valida la viabilidad de la siguiente idea de negocio, analizando:
                - Oportunidades de mercado
                - Retos o desafíos
                - Estrategias recomendadas para su éxito
                
                Idea de negocio: {idea_negocio}
                """

                try:
                    model = gen_ai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        generation_config=generation_config,
                        system_instruction="Eres un validador de ideas de negocio."
                    )

                    chat_session = model.start_chat(history=[])

                    progress = st.progress(0)
                    for i in range(100):
                        time.sleep(0.05)
                        progress.progress(i + 1)

                    gemini_response = chat_session.send_message(prompt)

                    st.markdown(f"## Validación de la idea de negocio:\n{gemini_response.text}")
                except Exception as e:
                    st.error(f"Ocurrió un error al validar la idea de negocio: {str(e)}")
