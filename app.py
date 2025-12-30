import streamlit as st
import re
import random
import unicodedata
from nltk.chat.util import Chat, reflections
def normalizar(texto):
  texto = texto.lower()
  texto = ''.join(
      c for c in unicodedata.normalize('NFD', texto)
      if unicodedata.category(c) != 'Mn'
  )
  return texto
patterns = [

    (
        r'.*(hola|holi|hey|buenas).*',
        ['Hola 💖 ¿cómo te sientes hoy?']
    ),

    (
        r'.*(bien|feliz|content).*',
        ['Me alegra mucho leer eso 🥹']
    ),

    (
        r'.*(triste|mal|deprimid|bajonead|vaci).*',
        ['Siento que te sientas así 🫂 Estoy aquí contigo']
    ),

    (
        r'.*(ansiedad|ansios|estres|estresad).*',
        ['Respira conmigo un momento 🫁 Estoy aquí']
    ),

    (
        r'.*(cansad|agotad|no doy mas).*',
        ['Has cargado mucho 💔 Descansar también es necesario']
    ),

    (
        r'.*',
        ['Estoy aquí contigo 🫂 cuéntame más si quieres']
    )
]
chatbot = Chat(patterns, reflections)
if 'estado_emocional' not in st.session_state:
  st.session_state.estado_emocional = None

if 'contador_preguntas' not in st.session_state:
  st.session_state.contador_preguntas = 0

if 'mensajes' not in st.session_state:
  st.session_state.mensajes = []
preguntas_apertura = {
    'triste': [
        '¿Quieres contarme qué es lo que más te duele ahora?',
        'Estoy aquí, ¿qué pasó?'
    ],
    'ansioso': [
        '¿Qué es lo que te tiene más inquieta ahora?',
        'Cuéntame qué te está rondando la cabeza'
    ],
    'cansado': [
        '¿Qué es lo que más te ha agotado últimamente?'
    ]
}
st.set_page_config(page_title="Chatbot emocional 💖", page_icon="💖")

st.title("🤍 Estoy aquí para ti")
st.caption("Este es un espacio seguro para expresar cómo te sientes")
for autor, texto in st.session_state.mensajes:
  with st.chat_message(autor):
      st.markdown(texto)
user_input = st.chat_input("Escribe cómo te sientes…")
if user_input:
  user_input_norm = normalizar(user_input)

  st.session_state.mensajes.append(("user", user_input))

  # Detectar estado emocional
  if re.search(r'.*(triste|mal|deprimid|bajonead|vaci).*', user_input_norm):
      st.session_state.estado_emocional = 'triste'

  elif re.search(r'.*(ansiedad|ansios|estres|estresad).*', user_input_norm):
      st.session_state.estado_emocional = 'ansioso'

  elif re.search(r'.*(cansad|agotad|no doy mas).*', user_input_norm):
      st.session_state.estado_emocional = 'cansado'

  # 💖 Gracias con contexto
  if re.search(r'.*(gracias|muchas gracias|thank).*', user_input_norm):
      if st.session_state.estado_emocional in ['triste', 'ansioso', 'cansado']:
          respuesta = "Gracias a ti por abrirte 🫂 de verdad"
      else:
          respuesta = "Siempre 💖 no hay de qué"

  # 🫂 Apertura de conversación (una vez)
  elif st.session_state.estado_emocional and st.session_state.contador_preguntas < 1:
      respuesta = random.choice(
          preguntas_apertura[st.session_state.estado_emocional]
      )
      st.session_state.contador_preguntas += 1

  else:
      respuesta = chatbot.respond(user_input_norm)

  st.session_state.mensajes.append(("assistant", respuesta))

