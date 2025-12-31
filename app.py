import streamlit as st
import random
import re
from nltk.chat.util import Chat, reflections
import os
import openai

def normalizar(texto):
    return texto.lower().strip()
# ------------------------------
# CONFIGURACIÓN IA
# ------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
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

if "pronombres" not in st.session_state:
    st.session_state.pronombres = None

# ------------------------------
# PREGUNTA INICIAL DE PRONOMBRES
# ------------------------------
if st.session_state.pronombres is None:
    st.info("🌸 Hola 🤍 Antes de empezar, ¿quieres que use pronombres femeninos, masculinos o neutros para hablar contigo?")
    pronombre_seleccionado = st.radio(
        "Elige tus pronombres:",
        options=["Femeninos", "Masculinos", "Neutros"]
    )
    if st.button("Empezar chat"):
        st.session_state.pronombres = pronombre_seleccionado

# Solo mostrar el chat si ya eligió pronombres
if st.session_state.pronombres:

    # ------------------------------
    # INTERFAZ STREAMLIT
    # ------------------------------
    st.title("🤍 Estoy aquí para ti")
    st.caption("Este es un espacio seguro para expresar cómo te sientes")

    # ------------------------------
    # MENSAJE DE BIENVENIDA
    # ------------------------------
    if not st.session_state.mensajes:
        st.info("🌸 Hola 🤍 Bienvenida, aquí puedes contarme cómo te sientes 🌸")

    # ------------------------------
    # HISTORIAL DE MENSAJES CON BURBUJAS COZY
    # ------------------------------
    for autor, texto in st.session_state.mensajes:
        if autor == "user":
            with st.chat_message("user"):
                st.markdown(
                    f"<div style='background-color:#FFE4E1; color:#000; padding:12px 16px; border-radius:20px; max-width:75%; font-size:16px; line-height:1.4;'>{texto}</div>",
                    unsafe_allow_html=True
                )
        else:
            with st.chat_message("assistant"):
                st.markdown(
                    f"<div style='background-color:#E0FFFF; color:#000; padding:12px 16px; border-radius:20px; max-width:75%; font-size:16px; line-height:1.4;'>{texto}</div>",
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
                f"<div style='background-color:#FFE4E1; color:#000; padding:12px 16px; border-radius:20px; max-width:75%; font-size:16px; line-height:1.4;'>{user_input}</div>",
                unsafe_allow_html=True
            )

        # ------------------------------
        # DETECTAR EMOCIONES
        # ------------------------------
        emocion_detectada = None
        if re.search(r'.*(triste|mal|deprimid|bajonead|vaci).*', user_input_norm):
            emocion_detectada = 'triste'
            st.session_state.contador_preguntas += 1

        elif re.search(r'.*(ansiedad|ansios|estres).*', user_input_norm):
            emocion_detectada = 'ansioso'
            st.session_state.contador_preguntas += 1

        elif re.search(r'.*(cansad|agotad).*', user_input_norm):
            emocion_detectada = 'cansado'
            st.session_state.contador_preguntas += 1

        # ------------------------------
        # DESPEDIDA Y AGRADECIMIENTO
        # ------------------------------
        if re.search(r'.*(gracias).*', user_input_norm):
            respuesta = "Gracias a ti por confiar 🤍"
        elif re.search(r'.*(adiós|chau|nos vemos|hasta luego).*', user_input_norm):
            respuesta = "💖 Gracias por hablar conmigo, cuídate mucho 🤍 ¡Hasta pronto!"
        else:
            # Si hay emoción, la IA responde empáticamente usando pronombres seleccionados
            if emocion_detectada:
                respuesta = obtener_respuesta_ia(user_input, contexto_emocional=emocion_detectada, pronombres=st.session_state.pronombres)
            else:
                # Primero intenta el chatbot clásico
                resp_chatbot = chatbot.respond(user_input_norm)
                if resp_chatbot:
                    respuesta = resp_chatbot
                else:
                    # Si no hay respuesta, usa IA normal
                    respuesta = obtener_respuesta_ia(user_input, pronombres=st.session_state.pronombres)

        # ------------------------------
        # MOSTRAR RESPUESTA INMEDIATAMENTE
        # ------------------------------
        st.session_state.mensajes.append(("assistant", respuesta))
        with st.chat_message("assistant"):
            st.markdown(
                f"<div style='background-color:#E0FFFF; color:#000; padding:12px 16px; border-radius:20px; max-width:75%; font-size:16px; line-height:1.4;'>{respuesta}</div>",
                unsafe_allow_html=True
            )
