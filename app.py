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
# Mostrar contenido para "Otra Opción"
if st.session_state.active_option == "Otra Opción":
    st.subheader("CREA Y PLANIFICA CON INGENIAR")
    
    # Copia tu código aquí
    import google.generativeai as gen_ai
    import time
    import PyPDF2

    # Configura Streamlit
    st.set_page_config(
        page_title="CREA Y PLANIFICA CON INGENIAR",
        page_icon=":lightbulb:",
        layout="centered",
    )

    # Obtén la clave API de las variables de entorno
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

    # Configura el modelo de Google Gemini
    gen_ai.configure(api_key=GOOGLE_API_KEY)

    # Configuración de generación
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }

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
                
              
   

