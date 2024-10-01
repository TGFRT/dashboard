import streamlit as st
import pandas as pd

# Configuración de la aplicación
st.set_page_config(
    page_title="Inicio de Sesión",
    page_icon="🔒",
    layout="centered"
)

# ID de Google Sheets
gsheetid = '1OVVjcFBFDOYcbmfqriYmfRke2MexzbjSvbknTwcnatk'
url = f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid=0'

# Cargar datos
try:
    dfUsuarios = pd.read_csv(url)
    dfUsuarios['celular'] = dfUsuarios['celular'].astype(str).str.replace(',', '')
    dfUsuarios['contrasena'] = dfUsuarios['contrasena'].astype(str).str.replace(',', '')
except Exception as e:
    st.error(f"Error al cargar los datos: {e}")

# Estilos CSS para mejorar el diseño
st.markdown("""<style>
    body {
        background-color: #f0f2f5;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        margin: 0;
    }
    .login-form {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
        width: 300px;
        background: white;
        border-radius: 10px;
    }
    .login-form h2 {
        margin-bottom: 20px;
        color: #ff9800;
        text-align: left;
    }
    .login-form input {
        width: 100%;
        padding: 10px;
        margin: 10px 0;
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    .login-form button {
        background-color: #ff9800;
        color: white;
        border: none;
        padding: 10px;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .login-form button:hover {
        background-color: #fb8c00;
    }
</style>""", unsafe_allow_html=True)

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
        st.write(f"Sueño: {row['suenos']} - Nivel: {row['nivel']}")
        
        # Mostrar objetivos como checkboxes
        objetivos_lista = row['respuestas'].split('\n') if pd.notna(row['respuestas']) else []
        for objetivo in objetivos_lista:
            if st.checkbox(objetivo):
                # Al marcar el objetivo, actualizar la lista en Google Sheets
                actualizar_objetivos(row['nombre'], row['suenos'], objetivo)  # Implementa esta función

else:
    # Sección de inicio de sesión
    st.markdown("<div class='login-form'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: left;'>Iniciar Sesión ⭐</h2>", unsafe_allow_html=True)

    celular = st.text_input("Número de Celular:")
    contrasena = st.text_input("Contraseña:", type="password")

    # Verificar si el celular y la contraseña son correctos
    if st.button("Iniciar Sesión"):
        celular_input = celular.replace(',', '')
        if celular_input in dfUsuarios['celular'].values:
            fila = dfUsuarios[dfUsuarios['celular'] == celular_input]
            if fila['contrasena'].values[0] == contrasena:
                # Guardar datos en la sesión
                st.session_state['nombre_usuario'] = fila['nombre'].values[0]
                st.experimental_rerun()  # Recargar la página para reflejar el nuevo estado
            else:
                st.error("Contraseña incorrecta", icon="❌")
        else:
            st.error("Número de celular no encontrado", icon="❌")

    st.markdown("</div>", unsafe_allow_html=True)
