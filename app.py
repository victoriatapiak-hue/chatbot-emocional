# ------------------------------
# IMPORTS
# ------------------------------
import streamlit as st
import random
import re
import os
import nltk
from nltk.chat.util import Chat, reflections
nltk.download('punkt')
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

def detectar_tema(texto):
    if re.search(r"(mamá|madre|papá|padre|hermano|hermana|familia)", texto):
        return "familia"
    if re.search(r"(u|universidad|estudio|prueba|examen)", texto):
        return "estudio"
    if re.search(r"(pareja|polola|pololo|relación)", texto):
        return "relaciones"
    if re.search(r"(trabajo|pega|jefe)", texto):
        return "trabajo"
    if re.search(r"(yo|autoestima|me siento inútil|no valgo)", texto):
        return "autoestima"
    return "general"

def tema_repetido(tema):
    ultimos= st.session_state.historial_temas[-3:]
    return ultimos.count(tema)>=2

def sugerir_micro_accion(emocion):
    acciones={
        "triste":"Si te parece, ahora mismo podríamos hacer algo muy chiquito: apoyar los pies en el suelo y respirar lento 10 segundos 🤍",
        "ansioso":"Tal vez podríamos pausar un segundo... inhala lento por la nariz y suelta despacio 🤍",
        "cansado":"Quizás ahora mismo solo necesitas aflojar los hombros y soltar un poco el cuerpo 🤍"
    }
    return acciones.get(emocion)
                 


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

if "historial_temas" not in st.session_state: 
    st.session_state.historial_temas = []
    
if "ultimo_estado_emocional" not in st.session_state:
    st.session_state.ultimo_estado_emocional = None
    
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

    # detectar tema
    tema_detectado = detectar_tema(user_input_norm)
    st.session_state.historial_temas.append(tema_detectado)

    alerta_repeticion = tema_repetido(tema_detectado)

    # memoria corta emoción
    memoria_emocional = ""
    if st.session_state.ultimo_estado_emocional and emocion_detectada:
        if st.session_state.ultimo_estado_emocional == emocion_detectada:
            memoria_emocional = f"Antes mencionaste sentirte {emocion_detectada}, y parece que eso sigue ahí 🤍 "

    st.session_state.ultimo_estado_emocional = emocion_detectada

    # cierres
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
                mensaje=memoria_emocional + user_input,
                contexto_emocional=emocion_detectada,
                pronombres=st.session_state.pronombres
            )

            if alerta_repeticion:
                respuesta += (
                    f"\n\nHe notado que el tema de {tema_detectado} aparece varias veces 🤍 "
                    "si quieres, podemos mirarlo con más calma."
                )

            micro = sugerir_micro_accion(emocion_detectada)
            if micro:
                respuesta += f"\n\n{micro}"

        else:
            respuesta = chatbot.respond(user_input_norm)
            if not respuesta:
                respuesta = obtener_respuesta_ia(
                    user_input,
                    pronombres=st.session_state.pronombres
                )

    st.session_state.mensajes.append(("assistant", respuesta))
    st.rerun()

