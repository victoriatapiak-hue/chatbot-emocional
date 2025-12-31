# ------------------------------
# IMPORTS
# ------------------------------
import streamlit as st
import random
import re
import os
from nltk.chat.util import Chat, reflections
from openai import OpenAI


# ------------------------------
# CONFIGURACIÓN OPENAI
# (LA API KEY VA EN STREAMLIT SECRETS)
# ------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ------------------------------
# FUNCIÓN IA
# ------------------------------
def obtener_respuesta_ia(mensaje, contexto_emocional=None, pronombres=None):
    prompt = mensaje

    if contexto_emocional:
        prompt = (
            f"El usuario se siente {contexto_emocional}. "
            f"Responde de forma empática, cálida y comprensiva: {mensaje}"
        )

    if pronombres:
        prompt += f" Usa pronombres {pronombres.lower()}."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return "Ups, algo falló con la IA 😅 pero sigo aquí contigo 🤍"


# ------------------------------
# FUNCIONES AUX
# ------------------------------
def normalizar(texto):
    return texto.lower().strip()


# ------------------------------
# DATOS DEL CHAT CLÁSICO (NLTK)
# ------------------------------
pairs = [
    [r"hola|holi|hey", ["Hola 🤍 estoy aquí contigo", "¡Hola! ¿Cómo te sientes hoy?"]],
    [r"gracias", ["Gracias a ti por abrirte 🫂", "De nada, me alegra escucharte 🤍"]],
    [r"(.*)", ["Gracias por compartir eso 💖", "Entiendo, sigue contándome"]]
]

chatbot = Chat(pairs, reflections)


# ------------------------------
# PREGUNTAS POR EMOCIÓN
# ------------------------------
preguntas_apertura = {
    "triste": [
        "¿Quieres contarme qué te tiene triste? 🥺",
        "Lo siento, ¿quieres hablar un poquito? 🤍"
    ],
    "ansioso": [
        "Vamos despacio, ¿qué te está generando ansiedad?",
        "Respira conmigo, ¿qué pasa por tu cabeza? 💛"
    ],
    "cansado": [
        "Suena a que estás agotada, ¿quieres hablarlo?",
        "¿Ha sido un día pesado? 😌"
    ]
}


# ------------------------------
# SESSION STATE
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
# SELECCIÓN DE PRONOMBRES
# ------------------------------
if st.session_state.pronombres is None:
    st.info("Hola 🤍 Antes de empezar, ¿qué pronombres prefieres?")
    pronombre_seleccionado = st.radio(
        "Elige una opción:",
        ["Femeninos", "Masculinos", "Neutros"]
    )

    if st.button("Empezar"):
        st.session_state.pronombres = pronombre_seleccionado
        st.rerun()


# ------------------------------
# INTERFAZ PRINCIPAL
# ------------------------------
if st.session_state.pronombres:

    st.title("🤍 Estoy aquí para ti")
    st.caption("Este es un espacio seguro para expresar cómo te sientes")

    if not st.session_state.mensajes:
        st.info("🌸 Hola 🤍 Puedes contarme cómo te sientes")


    # ------------------------------
    # MOSTRAR HISTORIAL
    # ------------------------------
    for autor, texto in st.session_state.mensajes:
        with st.chat_message(autor):
            bg = "#FFE4E1" if autor == "user" else "#E0FFFF"
            st.markdown(
                f"""
                <div style="
                    background-color:{bg};
                    color:#000;
                    padding:12px 16px;
                    border-radius:20px;
                    max-width:75%;
                    font-size:16px;
                ">
                {texto}
                </div>
                """,
                unsafe_allow_html=True
            )


    # ------------------------------
    # INPUT USUARIO
    # ------------------------------
    user_input = st.chat_input("Escribe cómo te sientes…")


    # ------------------------------
    # LÓGICA DEL CHAT
    # ------------------------------
    if user_input:
        user_input_norm = normalizar(user_input)

        # guardar mensaje usuario
        st.session_state.mensajes.append(("user", user_input))

        # detectar emoción
        emocion_detectada = None

        if re.search(r"(triste|mal|deprimid|bajonead|vaci)", user_input_norm):
            emocion_detectada = "triste"

        elif re.search(r"(ansiedad|ansios|estres)", user_input_norm):
            emocion_detectada = "ansioso"

        elif re.search(r"(cansad|agotad)", user_input_norm):
            emocion_detectada = "cansado"


        # despedidas
        if re.search(r"(adiós|chau|hasta luego)", user_input_norm):
            respuesta = "💖 Gracias por hablar conmigo, cuídate mucho 🤍"

        elif re.search(r"(gracias)", user_input_norm):
            respuesta = "Gracias a ti por confiar 🤍"

        else:
            if emocion_detectada:
                respuesta = obtener_respuesta_ia(
                    user_input,
                    contexto_emocional=emocion_detectada,
                    pronombres=st.session_state.pronombres
                )
            else:
                respuesta = chatbot.respond(user_input_norm)
                if not respuesta:
                    respuesta = obtener_respuesta_ia(
                        user_input,
                        pronombres=st.session_state.pronombres
                    )

        st.session_state.mensajes.append(("assistant", respuesta))
        st.rerun()
