import streamlit as st
import pandas as pd

# Configuración de la aplicación
st.set_page_config(
    page_title="Registro de Sueños",
    page_icon="🔒",
    layout="centered"
)

# ID de Google Sheets
gsheetid = '1OVVjcFBFDOYcbmfqriYmfRke2MexzbjSvbknTwcnatk'  # Reemplaza con tu ID
url = f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid=0'

# Cargar datos
try:
    dfUsuarios = pd.read_csv(url)
    dfUsuarios['celular'] = dfUsuarios['celular'].astype(str).str.replace(',', '')
    dfUsuarios['contrasena'] = dfUsuarios['contrasena'].astype(str).str.replace(',', '')
    
    # Imprimir las columnas para verificar
    st.write("Columnas de dfUsuarios:", dfUsuarios.columns.tolist())
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

# Verificar si el usuario ya ha iniciado sesión
if 'nombre_usuario' in st.session_state:
    nombre_usuario = st.session_state['nombre_usuario']

    # Registro de Sueños
    st.title("Registro de Sueños")
    
    nuevo_sueño = st.text_input("¿Qué sueño deseas alcanzar?")
    respuestas = st.text_area("Respuestas a las preguntas (separa cada respuesta por una línea)")

    if st.button("Registrar Sueño"):
        # Determinar nivel basado en las respuestas (implementa tu lógica aquí)
        nivel = calcular_nivel(respuestas)

        # Generar objetivos utilizando la IA (implementa la llamada a la IA aquí)
        objetivos = generar_objetivos(nuevo_sueño, nivel)

        # Guardar en Google Sheets (implementa esta función)
        guardar_en_sheets(nombre_usuario, nuevo_sueño, nivel, respuestas, objetivos)

        st.success("Sueño registrado correctamente!")

    # Mostrar los sueños existentes
    st.subheader("Tus Sueños")
    
    # Filtrar los sueños del usuario
    sueños_usuario = dfUsuarios[dfUsuarios['nombre'] == nombre_usuario]
    
    for index, row in sueños_usuario.iterrows():
        st.write(f"Sueño: {row['sueños']} - Nivel: {row['nivel']}")
        
        # Mostrar objetivos como checkboxes
        objetivos_lista = row['respuestas'].split('\n') if pd.notna(row['respuestas']) else []
        for objetivo in objetivos_lista:
            if st.checkbox(objetivo):
                # Al marcar el objetivo, actualizar la lista en Google Sheets
                actualizar_objetivos(row['nombre'], row['sueños'], objetivo)  # Implementa esta función

else:
    st.error("Por favor, inicia sesión para acceder a esta página.")
