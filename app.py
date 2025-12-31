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
# CONFIG STREAMLIT
# ------------------------------
st.set_page_config(page_title="Chatbot emocional", page_icon="🤍")


# ------------------------------
# CONFIGURACIÓN OPENAI
# ------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ------------------------------
# FUNCIÓN IA (tono controlado)
# ------------------------------
def obtener_respuesta_ia(mensaje, contexto_emocional=None, pronombres=None):
    prompt = (
        "Responde de forma empática, cercana y humana. "
        "No des discursos largos ni consejos forzados. "
        "Refleja lo que la persona siente y haz solo UNA pregunta suave.\n\n"
    )

    if contexto_emocional:
        prompt += f"La persona se siente {contexto_emocional}. "

    if pronombres:
        prompt += f"Usa pronombres {pronombres.lower()}. "

    prompt += f"Mensaje: {mensaje}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    except Exception:
        return "Ups, algo falló 😅 pero sigo aquí contigo 🤍"


# ------------------------------
# FUNCIONES AUX
# ------------------------------
def normalizar(texto):
    return texto.lower().strip()


# ------------------------------
# CHAT CLÁSICO (RESPUESTAS NO GENÉRICAS)
# ------------------------------
pairs = [
    [r"hola|holi|hey", [
        "Hola 🤍 estoy aquí contigo",
        "Hola 🤍 puedes tomarte tu tiempo para hablar"
    ]],
    [r"gracias", [
        "Gracias a ti por confiar 🤍",
        "Me alegra que estés aquí 🫂"
    ]],
    [r"(.*)", [
        "Te leo 🤍 ¿qué es lo que más te pesa ahora?",
        "Gracias por decirlo… ¿qué parte de esto es la más difícil?",
        "Estoy contigo, puedes seguir si quieres"
    ]]
]

chatbot = Chat(pairs, reflections)


# ------------------------------
# SESSION STATE
# ------------------------------
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

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

    # MENSAJE INICIAL + GUÍA (CAMBIO CLAVE)
    if not st.session_state.mensajes:
        st.info(
            "Estoy aquí para escucharte, sin apuro 🤍\n\n"
            "Si no sabes por dónde empezar, puedes escribir cosas como:\n"
            "“me siento…”, “hoy fue un día…” o “tengo esto dando vueltas en la cabeza”."
        )

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
    user_input = st.chat_input("Escribe lo que quieras compartir…")

    # ------------------------------
    # LÓGICA DEL CHAT
    # ------------------------------
    if user_input:
        user_input_norm = normalizar(user_input)
        st.session_state.mensajes.append(("user", user_input))

        emocion_detectada = None

        if re.search(r"(triste|mal|deprimid|bajonead|vaci)", user_input_norm):
            emocion_detectada = "triste"
        elif re.search(r"(ansiedad|ansios|estres)", user_input_norm):
            emocion_detectada = "ansioso"
        elif re.search(r"(cansad|agotad|abrumad)", user_input_norm):
            emocion_detectada = "cansado"

        # CIERRE BONITO (INTEGRACIÓN 5 💖)
        if re.search(r"(adiós|chau|hasta luego|me voy)", user_input_norm):
            respuesta = (
                "Gracias por compartir esto conmigo 🤍\n\n"
                "Tómate el tiempo que necesites. Puedes volver cuando quieras."
            )

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

