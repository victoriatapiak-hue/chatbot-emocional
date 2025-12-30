import streamlit as st
import random
import re
from nltk.chat.util import Chat, reflections

# ------------------------------
# FUNCIONES
# ------------------------------
def normalizar(texto):
    return texto.lower().strip()

# ------------------------------
# DATOS DEL CHAT
# ------------------------------
pairs = [
    [r"hola|holi|hey", ["Hola 🤍 estoy aquí contigo", "¡Hola! ¿Cómo te sientes hoy?"]],
    [r"gracias", ["Gracias a ti por abrirte 🫂", "De nada, me alegra poder escucharte 🤍"]],
    [r"(.*)", ["Gracias por compartir eso 💖", "Entiendo, sigue contándome"]]
]

chatbot = Chat(pairs, reflections)

preguntas_apertura = {
    "triste": ["¿Quieres contarme qué te tiene triste? 🥺", "Lo siento, ¿quieres hablar un poquito? 🤍"],
    "ansioso": ["Respira profundo, ¿quieres contarme qué te pone ansioso?", "Vamos despacio, ¿qué pasa por tu cabeza? 💛"],
    "cansado": ["Parece que necesitas descansar, ¿quieres que hablemos un rato tranquilamente?", "¿Quieres compartir cómo te sientes? 😌"]
}

# ------------------------------
# INICIALIZACIÓN DE SESSION_STATE
# ------------------------------
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if "estado_emocional" not in st.session_state:
    st.session_state.estado_emocional = None

if "contador_preguntas" not in st.session_state:
    st.session_state.contador_preguntas = 0

# ------------------------------
# INTERFAZ STREAMLIT
# ------------------------------
st.set_page_config(page_title="Chatbot emocional 💖", page_icon="💖")
st.title("🤍 Estoy aquí para ti")
st.caption("Este es un espacio seguro para expresar cómo te sientes")

# ------------------------------
# MENSAJE DE BIENVENIDA
# ------------------------------
if not st.session_state.mensajes:
    st.info("🌸 Hola 🤍 Bienvenida, aquí puedes contarme cómo te sientes 🌸")

# ------------------------------
# HISTORIAL DE MENSAJES CON BURBUJAS PASTEL
# ------------------------------
for autor, texto in st.session_state.mensajes:
    if autor == "user":
        with st.chat_message("user"):
            st.markdown(
                f"<div style='background-color:#FFD6E0; color:#000; padding:10px; border-radius:12px; max-width:80%;'>{texto}</div>",
                unsafe_allow_html=True
            )
    else:
        with st.chat_message("assistant"):
            st.markdown(
                f"<div style='background-color:#D6F0FF; color:#000; padding:10px; border-radius:12px; max-width:80%;'>{texto}</div>",
                unsafe_allow_html=True
            )

# ------------------------------
# INPUT DEL USUARIO
# ------------------------------
user_input = st.chat_input("Escribe cómo te sientes…")

# ------------------------------
# LÓGICA DEL CHAT
# ------------------------------
if user_input:
    user_input_norm = normalizar(user_input)

    # mostrar mensaje usuario
    st.session_state.mensajes.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(
            f"<div style='background-color:#FFD6E0; color:#000; padding:10px; border-radius:12px; max-width:80%;'>{user_input}</div>",
            unsafe_allow_html=True
        )

    # detectar emociones
    if re.search(r'.*(triste|mal|deprimid|bajonead|vaci).*', user_input_norm):
        st.session_state.estado_emocional = 'triste'
        respuesta = random.choice(preguntas_apertura['triste'])
        st.session_state.contador_preguntas += 1

    elif re.search(r'.*(ansiedad|ansios|estres).*', user_input_norm):
        st.session_state.estado_emocional = 'ansioso'
        respuesta = random.choice(preguntas_apertura['ansioso'])
        st.session_state.contador_preguntas += 1

    elif re.search(r'.*(cansad|agotad).*', user_input_norm):
        st.session_state.estado_emocional = 'cansado'
        respuesta = random.choice(preguntas_apertura['cansado'])
        st.session_state.contador_preguntas += 1

    elif re.search(r'.*(gracias).*', user_input_norm):
        respuesta = "Gracias a ti por confiar 🤍"
        
    # despedida
    elif re.search(r'.*(adiós|chau|nos vemos|hasta luego).*', user_input_norm):
         respuesta= "Gracias por hablar conmigo, cuídate muchooo, ¡Hasta pronto!💖."

    else:
        respuesta = chatbot.respond(user_input_norm)

    # mostrar respuesta inmediatamente
    st.session_state.mensajes.append(("assistant", respuesta))
    with st.chat_message("assistant"):
        st.markdown(
            f"<div style='background-color:#D6F0FF; color:#000; padding:10px; border-radius:12px; max-width:80%;'>{respuesta}</div>",
            unsafe_allow_html=True
        )
