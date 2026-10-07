# ------------------------------
# IMPORTS
# ------------------------------
import streamlit as st
import random
import re
import os
import nltk

from nltk.chat.util import Chat, reflections
from openai import OpenAI

nltk.download("punkt", quiet=True)


# ------------------------------
# CONFIGURACIÓN STREAMLIT
# ------------------------------
st.set_page_config(
    page_title="Chatbot emocional",
    page_icon="🤍"
)


# ------------------------------
# CONFIGURACIÓN OPENAI
# ------------------------------
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# ------------------------------
# FUNCIONES AUXILIARES
# ------------------------------

def normalizar(texto):
    """
    Convierte el texto a minúsculas y elimina
    espacios al inicio y al final.
    """
    return texto.lower().strip()


def detectar_tema(texto):
    """
    Detecta el tema principal del mensaje.
    """

    if re.search(
        r"(mamá|mama|madre|papá|papa|padre|"
        r"hermano|hermana|familia)",
        texto
    ):
        return "familia"

    if re.search(
        r"(universidad|estudio|estudiar|"
        r"prueba|examen|tarea|clase|profesor|profesora)",
        texto
    ):
        return "estudio"

    if re.search(
        r"(pareja|polola|pololo|novio|novia|"
        r"relación|relacion|amor|pareja)",
        texto
    ):
        return "relaciones"

    if re.search(
        r"(trabajo|pega|jefe|jefa|compañero|compañera|"
        r"oficina|turno|trabajar)",
        texto
    ):
        return "trabajo"

    if re.search(
        r"(autoestima|me siento inútil|"
        r"no valgo|no sirvo|soy insuficiente|"
        r"me odio|odio mi cuerpo)",
        texto
    ):
        return "autoestima"

    return "general"


def tema_repetido(tema):
    """
    Verifica si el mismo tema se ha mencionado
    varias veces recientemente.
    """

    ultimos = st.session_state.historial_temas[-3:]

    return ultimos.count(tema) >= 2


def sugerir_micro_accion(emocion):
    """
    Devuelve una pequeña acción según la emoción detectada.
    """

    acciones = {

        "triste":
            "Si te parece, ahora mismo podríamos hacer algo muy chiquito: "
            "apoyar los pies en el suelo y respirar lento unos segundos 🤍",

        "ansioso":
            "Tal vez podríamos pausar un segundo... "
            "inhala lento por la nariz y suelta despacio 🤍",

        "cansado":
            "Quizás ahora mismo solo necesitas aflojar los hombros "
            "y soltar un poquito el cuerpo 🤍"
    }

    return acciones.get(emocion)


# ------------------------------
# FALLBACK CLÁSICO
# ------------------------------

pairs = [

    [
        r"hola|holi|hey",
        [
            "Hola 🤍 estoy aquí contigo.",
            "Hola 🤍 puedes tomarte tu tiempo para hablar."
        ]
    ],

    [
        r"gracias",
        [
            "Gracias a ti por confiar 🤍",
            "Me alegra que estés aquí 🫂"
        ]
    ],

    [
        r"(.*)",
        [
            "Te leo 🤍 Puedes seguir contándome si quieres.",
            "Estoy aquí contigo 🤍",
            "Puedes tomarte tu tiempo para contarme lo que pasó."
        ]
    ]
]

chatbot = Chat(
    pairs,
    reflections
)


# ------------------------------
# OBTENER RESPUESTA DE LA IA
# ------------------------------

def obtener_respuesta_ia(
    mensaje,
    contexto_emocional=None,
    tema=None,
    pronombres=None
):
    """
    Obtiene una respuesta de OpenAI utilizando
    el contexto emocional y el historial reciente.
    """

    # ------------------------------------------
    # PERSONALIDAD E INSTRUCCIONES DEL CHATBOT
    # ------------------------------------------

    instrucciones = """
Eres un chatbot emocional cálido, cercano, empático y humano.

Tu objetivo no es simplemente responder mensajes:
tu objetivo es acompañar una conversación.

La persona debe sentir que está siendo escuchada
y que estás prestando atención a lo que realmente acaba
de contarte.

REGLAS DE CONVERSACIÓN:

1. Responde específicamente a lo que la persona acaba de decir.

2. Ten en cuenta los mensajes anteriores para mantener
   continuidad en la conversación.

3. Recuerda el contexto emocional de la conversación.

4. No respondas como un terapeuta robótico, un manual
   de autoayuda o un formulario.

5. Evita frases genéricas y repetitivas como:
   "entiendo que te sientas así"
   si no aportan algo concreto a la conversación.

6. No intentes solucionar inmediatamente todo lo que
   la persona está contando.

7. Primero escucha y valida cuando corresponda.

8. Puedes desarrollar tus respuestas en varios párrafos
   cuando la situación lo necesite.

9. No existe una longitud obligatoria para las respuestas.
   Sé breve cuando corresponda y más expresivo cuando
   la conversación lo necesite.

10. NO hagas una pregunta al final de cada respuesta.

11. Puedes hacer una pregunta cuando realmente ayude
    a profundizar o continuar naturalmente la conversación.

12. Si la persona está contando una historia, reacciona
    a los detalles importantes de esa historia.

13. Si expresa emociones contradictorias, reconoce esa
    complejidad en lugar de simplificar lo que siente.

14. Mantén un tono natural, cálido, conversacional
    y expresivo.

15. Puedes utilizar emojis ocasionalmente cuando encajen
    de forma natural, pero no abuses de ellos.

16. No repitas constantemente la misma estructura
    de respuesta.

17. No conviertas cada mensaje en una sesión de preguntas.

18. Si la persona simplemente quiere desahogarse,
    permítele hacerlo.

19. Si la persona necesita apoyo emocional, acompáñala
    sin sonar exageradamente formal.

20. Habla como alguien que está realmente presente
    en la conversación.
    """


    # ------------------------------------------
    # CONTEXTO ADICIONAL
    # ------------------------------------------

    contexto = ""

    if contexto_emocional:

        contexto += (
            "\nLa emoción detectada actualmente es: "
            f"{contexto_emocional}."
        )

    if tema:

        contexto += (
            "\nEl tema detectado actualmente es: "
            f"{tema}."
        )

    if pronombres:

        contexto += (
            "\nUtiliza pronombres correspondientes a: "
            f"{pronombres.lower()}."
        )


    # ------------------------------------------
    # CONSTRUIR HISTORIAL RECIENTE
    # ------------------------------------------

    historial = []

    # Tomamos solamente los últimos 12 mensajes
    # para mantener el contexto sin hacerlo enorme.

    for autor, texto in st.session_state.mensajes[-12:]:

        if autor == "user":

            historial.append({
                "role": "user",
                "content": texto
            })

        elif autor == "assistant":

            historial.append({
                "role": "assistant",
                "content": texto
            })


    # ------------------------------------------
    # CONSTRUIR MENSAJES PARA OPENAI
    # ------------------------------------------

    mensajes = [

        {
            "role": "system",
            "content": instrucciones + contexto
        }

    ]

    mensajes.extend(historial)


    # ------------------------------------------
    # EVITAR DUPLICAR EL MENSAJE ACTUAL
    # ------------------------------------------

    if not historial or historial[-1]["content"] != mensaje:

        mensajes.append({

            "role": "user",
            "content": mensaje

        })


    # ------------------------------------------
    # LLAMADA A OPENAI
    # ------------------------------------------

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=mensajes,

            temperature=0.85,

            max_tokens=500
        )

        respuesta = response.choices[0].message.content

        if respuesta:

            return respuesta.strip()

        return chatbot.respond(
            normalizar(mensaje)
        )

    except Exception as e:

        # Mostrar el error en la consola de Streamlit
        # para poder saber qué ocurrió.

        print(
            f"Error al comunicarse con OpenAI: {e}"
        )

        # --------------------------------------
        # FALLBACK
        # --------------------------------------

        respuesta_fallback = chatbot.respond(
            normalizar(mensaje)
        )

        if respuesta_fallback:

            return respuesta_fallback

        return (
            "Ups, parece que tuve un pequeño problema 😅 "
            "pero sigo aquí contigo 🤍"
        )


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


if "alerta_disparada" not in st.session_state:

    st.session_state.alerta_disparada = {}


if "nuevo_input" not in st.session_state:

    st.session_state.nuevo_input = False


# ------------------------------
# SELECCIÓN DE PRONOMBRES
# ------------------------------

if st.session_state.pronombres is None:

    st.info(
        "Hola 🤍 Antes de empezar, "
        "¿qué pronombres prefieres?"
    )

    pronombre_seleccionado = st.radio(
        "Elige una opción:",
        [
            "Femeninos",
            "Masculinos",
            "Neutros"
        ]
    )

    if st.button("Empezar"):

        st.session_state.pronombres = (
            pronombre_seleccionado
        )

        st.rerun()


# ------------------------------
# INTERFAZ PRINCIPAL
# ------------------------------

if st.session_state.pronombres:

    st.title("🤍 Estoy aquí para ti")

    st.caption(
        "Este es un espacio seguro para expresar "
        "cómo te sientes"
    )


    # ------------------------------------------
    # MENSAJE INICIAL
    # ------------------------------------------

    if not st.session_state.mensajes:

        st.info(
            "Estoy aquí para escucharte, sin apuro 🤍\n\n"
            "Si no sabes por dónde empezar, puedes escribir cosas como:\n"
            "“me siento…”, “hoy fue un día…” o "
            "“tengo esto dando vueltas en la cabeza”."
        )


    # ------------------------------------------
    # MOSTRAR HISTORIAL
    # ------------------------------------------

    for autor, texto in st.session_state.mensajes:

        with st.chat_message(autor):

            if autor == "user":

                bg = "#FFE4E1"

            else:

                bg = "#E0FFFF"

            st.markdown(

                f"""
                <div style="
                    background-color:{bg};
                    padding:12px 16px;
                    border-radius:20px;
                    max-width:75%;
                ">
                    {texto}
                </div>
                """,

                unsafe_allow_html=True
            )


    # ------------------------------------------
    # INPUT USUARIO
    # ------------------------------------------

    user_input = st.chat_input(
        "Escribe lo que quieras compartir…"
    )


    if user_input:

        st.session_state.nuevo_input = True

        user_input_norm = normalizar(
            user_input
        )


        # --------------------------------------
        # GUARDAR MENSAJE DEL USUARIO
        # --------------------------------------

        st.session_state.mensajes.append(
            ("user", user_input)
        )


        # --------------------------------------
        # DETECCIÓN DE EMOCIÓN
        # --------------------------------------

        emocion_detectada = None


        if re.search(
            r"(triste|mal|deprimid|bajonead|vaci)",
            user_input_norm
        ):

            emocion_detectada = "triste"


        elif re.search(
            r"(ansiedad|ansios|estres|nervios|angustia)",
            user_input_norm
        ):

            emocion_detectada = "ansioso"


        elif re.search(
            r"(cansad|agotad|abrumad|sin energía)",
            user_input_norm
        ):

            emocion_detectada = "cansado"


        # --------------------------------------
        # DETECCIÓN DE TEMA
        # --------------------------------------

        tema_detectado = detectar_tema(
            user_input_norm
        )

        st.session_state.historial_temas.append(
            tema_detectado
        )


        # --------------------------------------
        # ALERTA SUAVE POR REPETICIÓN DE TEMA
        # --------------------------------------

        alerta_repeticion = tema_repetido(
            tema_detectado
        )


        if (
            alerta_repeticion
            and not st.session_state.alerta_disparada.get(
                tema_detectado,
                False
            )
        ):

            alerta_msg = (
                f"\n\nHe notado que el tema de "
                f"{tema_detectado} aparece varias veces 🤍 "
                "Si quieres, podemos mirarlo con más calma."
            )

            st.session_state.alerta_disparada[
                tema_detectado
            ] = True

        else:

            alerta_msg = ""


        # --------------------------------------
        # CIERRES CONSCIENTES
        # --------------------------------------

        if re.search(
            r"(adiós|adios|chau|hasta luego|me voy)",
            user_input_norm
        ):

            respuesta = (
                "Gracias por compartir esto conmigo 🤍\n\n"
                "Tómate el tiempo que necesites. "
                "Puedes volver cuando quieras."
            )


        elif re.search(
            r"^(gracias|muchas gracias)$",
            user_input_norm
        ):

            respuesta = (
                "Gracias a ti por confiar en mí 🤍"
            )


        else:

            # ----------------------------------
            # RESPUESTA PRINCIPAL DE OPENAI
            # ----------------------------------

            respuesta = obtener_respuesta_ia(

                mensaje=user_input,

                contexto_emocional=(
                    emocion_detectada
                ),

                tema=tema_detectado,

                pronombres=(
                    st.session_state.pronombres
                )
            )


            # ----------------------------------
            # ALERTA DE TEMA REPETIDO
            # ----------------------------------

            if alerta_msg:

                respuesta += alerta_msg


            # ----------------------------------
            # MICRO ACCIÓN OCASIONAL
            # ----------------------------------

            micro = sugerir_micro_accion(
                emocion_detectada
            )


            # Solo aparece algunas veces para
            # evitar respuestas repetitivas.

            if (
                micro
                and random.random() < 0.30
            ):

                respuesta += (
                    f"\n\n{micro}"
                )


        # --------------------------------------
        # GUARDAR RESPUESTA
        # --------------------------------------

        st.session_state.mensajes.append(
            ("assistant", respuesta)
        )


        # --------------------------------------
        # RERUN CONTROLADO
        # --------------------------------------

        if st.session_state.nuevo_input:

            st.session_state.nuevo_input = False

            st.rerun()
