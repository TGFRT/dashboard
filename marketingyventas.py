import streamlit as st
import google.generativeai as gen_ai
import requests
import io
from PIL import Image
import random
from googletrans import Translator
import time
import PyPDF2  # Asegúrate de tener esta importación para manejar PDFs

# Configura Streamlit
st.set_page_config(page_title="CREADOR DE MARKETING CON INGENIAR", page_icon=":rocket:", layout="centered")

# Obtén la clave API de las variables de entorno
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
gen_ai.configure(api_key=GOOGLE_API_KEY)

# Configuración de generación
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

# Función para hacer la solicitud a la API de Hugging Face para generar imágenes
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
