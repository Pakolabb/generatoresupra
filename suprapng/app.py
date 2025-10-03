import streamlit as st
from PIL import Image
import os

# Percorso del file logo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_file = "Logoopacita1.png"
logo_path = os.path.join(BASE_DIR, logo_file)

st.title("Test Logo 🔍")

# Carica e mostra il logo
if os.path.exists(logo_path):
    logo_img = Image.open(logo_path).convert("RGBA")

    # Ridimensiona proporzionalmente (50% larghezza canvas)
    canvas_w, canvas_h = 800, 600
    logo_w, logo_h = logo_img.size
    ratio = min(canvas_w/logo_w, canvas_h/logo_h) * 0.5
    new_size = (int(logo_w*ratio), int(logo_h*ratio))
    logo_img = logo_img.resize(new_size, Image.ANTIALIAS)

    # Crea canvas bianco
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 255))

    # Centra il logo
    x = (canvas_w - new_size[0]) // 2
    y = (canvas_h - new_size[1]) // 2
    canvas.paste(logo_img, (x, y), logo_img)

    # Mostra il risultato
    st.image(canvas, caption="Logo centrato", use_container_width=True)
else:
    st.error("Logo non trovato!")
