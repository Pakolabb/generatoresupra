import streamlit as st
from PIL import Image, ImageEnhance
import os
import random

# Cartelle parti variabili
folders = {
    "Tetto": "tetto",
    "Cofano": "cofano",
    "Carrozzeria": "carrozzeria",
    "Pinze": "pinza",
    "Cerchioni": "cerchioni",
}

# File fissi (logoopacita gestito a parte)
fixed_files = [
    "gomme.png",
    "ombra.png",
    "dettagli.png"
]

# Probabilità colori
color_probs = {
    "base": 0.83,
    "turchese": 0.07,
    "viola": 0.05,
    "cf": 0.04,
    "gold": 0.01
}

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

st.title("Generatore Supra 🎨")

if st.button("Genera Auto"):
    canvas = None
    report = {}

    # Trova prima immagine per dimensione canvas
    all_images = []
    for folder in folders.values():
        if os.path.exists(folder):
            all_images += [os.path.join(folder, f) for f in os.listdir(folder)]
    for f in fixed_files:
        if os.path.exists(f):
            all_images.append(f)

    if all_images:
        ref_img = Image.open(all_images[0]).convert("RGBA")
        canvas = Image.new("RGBA", ref_img.size, (255, 255, 255, 0))
    else:
        st.write("Nessuna immagine trovata!")
        canvas = None

    # Parti variabili
    for part, folder in folders.items():
        if os.path.exists(folder):
            files = os.listdir(folder)
            if files:
                chosen = choose_color(files)
                img = Image.open(os.path.join(folder, chosen)).convert("RGBA")
                canvas.alpha_composite(img)
                report[part] = os.path.splitext(chosen)[0]

    # File fissi
    for f in fixed_files:
        if os.path.exists(f):
            img = Image.open(f).convert("RGBA")
            canvas.alpha_composite(img)

    # Logoopacita sopra tutti
    logo_path = "logoopacita.png"
    if canvas and os.path.exists(logo_path):
        logo_img = Image.open(logo_path).convert("RGBA")

        # Ridimensiona proporzionalmente al canvas
        canvas_w, canvas_h = canvas.size
        logo_w, logo_h = logo_img.size
        ratio = min(canvas_w/logo_w, canvas_h/logo_h) * 0.5  # 50% del canvas
        new_size = (int(logo_w*ratio), int(logo_h*ratio))
        logo_img = logo_img.resize(new_size, Image.ANTIALIAS)

        # Aumenta visibilità se trasparente
        enhancer = ImageEnhance.Brightness(logo_img)
        logo_img = enhancer.enhance(2.0)  # raddoppia luminosità

        # Centra il logo
        layer = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
        x = (canvas_w - new_size[0]) // 2
        y = (canvas_h - new_size[1]) // 2
        layer.paste(logo_img, (x, y), logo_img)

        canvas.alpha_composite(layer)

        # Mostra logo separato per debug
        st.image(logo_img, caption="Logoopacita test", use_container_width=False)

    # Mostra canvas finale e report
    if canvas:
        st.image(canvas, caption="La tua Supra generata", use_container_width=True)
        st.subheader("Dettagli generazione:")
        for part, colore in report.items():
            st.write(f"**{part}** → {colore}")
