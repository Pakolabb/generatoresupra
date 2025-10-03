import streamlit as st
from PIL import Image, ImageEnhance
from PIL.Image import Resampling
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cartelle parti variabili
folders = {
    "Tetto": "tetto",
    "Cofano": "cofano",
    "Carrozzeria": "carrozzeria",
    "Pinze": "pinza",
    "Cerchioni": "cerchioni",
}

# File fissi (senza logo)
fixed_files = [
    "gomme.png",
    "ombra.png",
    "dettagli.png"
]

# File logo
logo_file = "Logoopacita1.png"

# Probabilità colori
color_probs = {
    "base": 0.83,
    "turchese": 0.07,
    "viola": 0.05,
    "cf": 0.04,
    "gold": 0.01
}

# Funzione scelta colore con probabilità
def choose_color(files):
    base_colors = [f for f in files if not any(x in f.lower() for x in ["turchese", "viola", "cf", "gold"])]
    turchese = [f for f in files if "turchese" in f.lower()]
    viola = [f for f in files if "viola" in f.lower()]
    cf = [f for f in files if "cf" in f.lower() or "fibra" in f.lower()]
    gold = [f for f in files if "gold" in f.lower()]

    choices, weights = [], []
    if base_colors:
        choices.append(random.choice(base_colors))
        weights.append(color_probs["base"])
    if turchese:
        choices.append(random.choice(turchese))
        weights.append(color_probs["turchese"])
    if viola:
        choices.append(random.choice(viola))
        weights.append(color_probs["viola"])
    if cf:
        choices.append(random.choice(cf))
        weights.append(color_probs["cf"])
    if gold:
        choices.append(random.choice(gold))
        weights.append(color_probs["gold"])

    return random.choices(choices, weights=weights, k=1)[0]

# Funzione watermark ripetuto
def apply_watermark_grid(canvas, logo_path, opacity=160, spacing=300):
    logo_img = Image.open(logo_path).convert("RGBA")
    logo_img = logo_img.resize((int(logo_img.width * 0.3), int(logo_img.height * 0.3)), Resampling.LANCZOS)

    alpha = logo_img.split()[3]
    alpha = alpha.point(lambda p: opacity)
    logo_img.putalpha(alpha)

    layer = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    for x in range(0, canvas.width, spacing):
        for y in range(0, canvas.height, spacing):
            layer.paste(logo_img, (x, y), logo_img)

    canvas.alpha_composite(layer)

# Funzione logo centrale
def apply_logo(canvas, logo_path):
    logo_img = Image.open(logo_path).convert("RGBA")
    canvas_w, canvas_h = canvas.size
    logo_w, logo_h = logo_img.size
    ratio = min(canvas_w/logo_w, canvas_h/logo_h) * 0.5
    new_size = (int(logo_w*ratio), int(logo_h*ratio))
    logo_img = logo_img.resize(new_size, Resampling.LANCZOS)

    layer = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    x = (canvas_w - new_size[0]) // 2
    y = (canvas_h - new_size[1]) // 2
    layer.paste(logo_img, (x, y), logo_img)
    canvas.alpha_composite(layer)

# Interfaccia Streamlit
st.title("Generatore Supra 🎨")

if st.button("Genera Auto"):
    canvas = None
    report = {}

    # Parti variabili
    for part, folder in folders.items():
        part_folder = os.path.join(BASE_DIR, folder)
        if os.path.exists(part_folder):
            files = [f for f in os.listdir(part_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            if files:
                chosen = choose_color(files)
                try:
                    img = Image.open(os.path.join(part_folder, chosen)).convert("RGBA")
                    if canvas is None:
                        canvas = Image.new("RGBA", img.size, (255, 255, 255, 0))
                    canvas.alpha_composite(img)
                    report[part] = os.path.splitext(chosen)[0]
                except Exception as e:
                    st.warning(f"Errore nel caricamento di {chosen}: {e}")

    # File fissi
    for f in fixed_files:
        fpath = os.path.join(BASE_DIR, f)
        if os.path.exists(fpath):
            img = Image.open(fpath).convert("RGBA")
            canvas.alpha_composite(img)

    # Applica watermark e logo
    if canvas:
        logo_path = os.path.join(BASE_DIR, logo_file)
        if os.path.exists(logo_path):
            apply_watermark_grid(canvas, logo_path)  # watermark ripetuto
            apply_logo(canvas, logo_path)            # logo centrale sopra tutto

        # Mostra canvas finale
        st.image(canvas, caption="La tua Supra generata", use_container_width=True)

        # Mostra report
        st.subheader("Dettagli generazione:")
        for part, colore in report.items():
            st.write(f"**{part}** → {colore}")
    else:
        st.write("Nessuna immagine trovata!")
