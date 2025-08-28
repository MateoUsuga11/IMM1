import streamlit as st
import os
import time
import glob
from gtts import gTTS
from PIL import Image
import base64
from langdetect import detect

# Título e imagen principal
st.title("Conversión de Texto a Audio")
image = Image.open('gato_raton.png')
st.image(image, width=350)

# Crear carpeta temporal si no existe
try:
    os.mkdir("temp")
except:
    pass

# --- Funciones auxiliares ---
def text_to_speech(text, tld, lang, slow):
    tts = gTTS(text, lang=lang, tld=tld, slow=slow)
    try:
        my_file_name = text[0:20].replace(" ", "_")
    except:
        my_file_name = "audio"
    filename = f"temp/{my_file_name}.mp3"
    tts.save(filename)
    return filename, text

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, "rb") as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

remove_files(7)

# --- Interfaz con pestañas ---
tab1, tab2, tab3 = st.tabs(["📖 Fábula", "✍️ Texto libre", "🎵 Audios guardados"])

with tab1:
    st.subheader("Una pequeña Fábula de Franz Kafka")
    st.write(
        '¡Ay! -dijo el ratón-. El mundo se hace cada día más pequeño. Al principio era tan grande que le tenía miedo. '
        'Corría y corría y por cierto que me alegraba ver esos muros, a diestra y siniestra, en la distancia. '
        'Pero esas paredes se estrechan tan rápido que me encuentro en el último cuarto y ahí en el rincón está '
        'la trampa sobre la cual debo pasar. Todo lo que debes hacer es cambiar de rumbo dijo el gato... y se lo comió. '
    )
    default_text = ("¡Ay! -dijo el ratón-. El mundo se hace cada día más pequeño..."
                    " Franz Kafka.")
    st.session_state["selected_text"] = default_text

with tab2:
    st.subheader("Escribe tu propio texto")
    text = st.text_area("Ingrese el texto a escuchar:")
    if text:
        st.session_state["selected_text"] = text

with tab3:
    st.subheader("Audios guardados en carpeta")
    files = glob.glob("temp/*.mp3")
    if files:
        for file in files:
            st.audio(file)
            st.markdown(get_binary_file_downloader_html(file, file_label=os.path.basename(file)), unsafe_allow_html=True)
    else:
        st.info("Aún no hay audios guardados.")

# --- Configuración de voz ---
st.sidebar.subheader("Configuración de la voz")

# Acentos disponibles
accent = st.sidebar.selectbox("Selecciona acento/voz", ["com", "com.mx", "com.co", "co.uk", "com.au"])
# Velocidad
speed = st.sidebar.slider("Velocidad de la voz (lento → rápido)", 0.5, 2.0, 1.0)

# --- Botón de conversión ---
if "selected_text" in st.session_state and st.session_state["selected_text"].strip():
    text_input = st.session_state["selected_text"]

    # Detección automática del idioma
    try:
        lang_detected = detect(text_input)
    except:
        lang_detected = "es"  # fallback por defecto

    st.markdown(f"**Idioma detectado:** `{lang_detected}`")

    if st.button("Convertir a Audio"):
        filename, output_text = text_to_speech(
            text_input, 
            tld=accent, 
            lang=lang_detected, 
            slow=(speed < 1.0)
        )

        st.success("✅ Audio generado con éxito")
        st.audio(filename, format="audio/mp3", start_time=0)
        st.markdown(get_binary_file_downloader_html(filename, file_label="Descargar audio"), unsafe_allow_html=True)
